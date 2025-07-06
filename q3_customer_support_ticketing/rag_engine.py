import google.generativeai as genai
import chromadb
from chromadb.config import Settings
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from textblob import TextBlob
import numpy as np
from models import (
    TicketCategory, TicketPriority, SentimentType, 
    SimilarTicket, AutoResponse, TicketAnalysis
)
from database import SessionLocal, DBTicket, DBKnowledgeBase
import re

class RAGEngine:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize ChromaDB
        self.chroma_persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        self.client = chromadb.PersistentClient(path=self.chroma_persist_directory)
        
        # Collections
        self.tickets_collection = self.client.get_or_create_collection("tickets")
        self.knowledge_collection = self.client.get_or_create_collection("knowledge_base")
        
        # Configuration
        self.max_similar_tickets = int(os.getenv("MAX_SIMILAR_TICKETS", "5"))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        self.escalation_threshold = float(os.getenv("ESCALATION_THRESHOLD", "0.3"))
        
        # Initialize knowledge base
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with sample e-commerce data"""
        sample_knowledge = [
            {
                "title": "Return Policy",
                "content": "Our return policy allows customers to return products within 30 days of purchase. Items must be in original condition with all packaging. Refunds will be processed within 5-7 business days.",
                "category": "returns",
                "tags": ["return", "refund", "policy", "30 days"]
            },
            {
                "title": "Shipping Information",
                "content": "Standard shipping takes 3-5 business days. Express shipping (1-2 days) is available for an additional fee. International shipping available to select countries.",
                "category": "shipping",
                "tags": ["shipping", "delivery", "express", "international"]
            },
            {
                "title": "Payment Issues",
                "content": "If payment fails but money is deducted, please contact us immediately. We will investigate and process a refund if the transaction was not completed. Provide order number and transaction ID.",
                "category": "payment",
                "tags": ["payment", "failed", "refund", "transaction"]
            },
            {
                "title": "Damaged Products",
                "content": "If you receive a damaged product, take photos and contact us within 48 hours. We will arrange a replacement or refund. Do not discard the original packaging.",
                "category": "damaged",
                "tags": ["damaged", "replacement", "photos", "packaging"]
            },
            {
                "title": "Account Management",
                "content": "You can update your account information, change password, and view order history in your account dashboard. For security issues, contact support immediately.",
                "category": "account",
                "tags": ["account", "password", "security", "dashboard"]
            }
        ]
        
        # Add to database and vector store
        db = SessionLocal()
        try:
            for item in sample_knowledge:
                # Check if already exists
                existing = db.query(DBKnowledgeBase).filter(
                    DBKnowledgeBase.title == item["title"]
                ).first()
                
                if not existing:
                    kb_entry = DBKnowledgeBase(
                        title=item["title"],
                        content=item["content"],
                        category=item["category"],
                        tags=json.dumps(item["tags"])
                    )
                    db.add(kb_entry)
                    db.commit()
                    
                    # Add to vector store
                    self.knowledge_collection.add(
                        documents=[item["content"]],
                        metadatas=[{"title": item["title"], "category": item["category"]}],
                        ids=[f"kb_{kb_entry.id}"]
                    )
        finally:
            db.close()
    
    def analyze_ticket(self, subject: str, description: str) -> TicketAnalysis:
        """Analyze ticket for categorization, priority, sentiment, and tags"""
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(description)
        
        # Categorization
        category, category_confidence = self._categorize_ticket(subject, description)
        
        # Priority assignment
        priority = self._assign_priority(subject, description, sentiment, category)
        
        # Tag generation
        tags = self._generate_tags(subject, description, category)
        
        # Overall confidence
        confidence_score = category_confidence
        
        # Escalation logic
        escalation_needed = (
            confidence_score < self.escalation_threshold or
            priority in [TicketPriority.HIGH, TicketPriority.URGENT] or
            sentiment == SentimentType.NEGATIVE
        )
        
        return TicketAnalysis(
            category=category,
            priority=priority,
            sentiment=sentiment,
            tags=tags,
            confidence_score=confidence_score,
            escalation_needed=escalation_needed
        )
    
    def _analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of the ticket text"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return SentimentType.POSITIVE
        elif polarity < -0.1:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
    
    def _categorize_ticket(self, subject: str, description: str) -> Tuple[TicketCategory, float]:
        """Categorize ticket using Gemini"""
        
        prompt = f"""
        Analyze the following customer support ticket and categorize it into one of these categories:
        - shipping_issue: Problems with delivery, tracking, or shipping
        - payment_problem: Payment failures, billing issues, refunds
        - product_return: Return requests, exchange requests
        - technical_support: Website issues, app problems, technical difficulties
        - account_issue: Login problems, account access, profile issues
        - general_inquiry: General questions, information requests
        - refund_request: Specific refund requests
        - damaged_product: Products received damaged or defective
        
        Subject: {subject}
        Description: {description}
        
        Respond with only the category name and a confidence score (0-1) separated by a comma.
        Example: shipping_issue,0.85
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip().split(',')
            category_name = result[0].strip()
            confidence = float(result[1].strip())
            
            return TicketCategory(category_name), confidence
        except Exception as e:
            print(f"Error in categorization: {e}")
            return TicketCategory.GENERAL_INQUIRY, 0.5
    
    def _assign_priority(self, subject: str, description: str, sentiment: SentimentType, category: TicketCategory) -> TicketPriority:
        """Assign priority based on content analysis"""
        
        # Keywords that indicate high priority
        urgent_keywords = ['urgent', 'emergency', 'broken', 'not working', 'failed', 'error', 'critical']
        high_keywords = ['important', 'need help', 'problem', 'issue', 'trouble', 'difficulty']
        
        text = f"{subject} {description}".lower()
        
        # Check for urgent keywords
        if any(keyword in text for keyword in urgent_keywords):
            return TicketPriority.URGENT
        
        # Check for high priority indicators
        if any(keyword in text for keyword in high_keywords):
            return TicketPriority.HIGH
        
        # Category-based priority
        if category in [TicketCategory.PAYMENT_PROBLEM, TicketCategory.DAMAGED_PRODUCT]:
            return TicketPriority.HIGH
        
        # Sentiment-based priority
        if sentiment == SentimentType.NEGATIVE:
            return TicketPriority.MEDIUM
        
        return TicketPriority.LOW
    
    def _generate_tags(self, subject: str, description: str, category: TicketCategory) -> List[str]:
        """Generate relevant tags for the ticket"""
        
        prompt = f"""
        Generate 3-5 relevant tags for this customer support ticket. Tags should be single words or short phrases that help categorize and search the ticket.
        
        Subject: {subject}
        Description: {description}
        Category: {category.value}
        
        Respond with only the tags separated by commas.
        Example: order,shipping,delayed
        """
        
        try:
            response = self.model.generate_content(prompt)
            tags = [tag.strip() for tag in response.text.strip().split(',')]
            return tags[:5]  # Limit to 5 tags
        except Exception as e:
            print(f"Error in tag generation: {e}")
            return [category.value]
    
    def find_similar_tickets(self, subject: str, description: str, limit: int = None) -> List[SimilarTicket]:
        """Find similar historical tickets using vector similarity"""
        
        if limit is None:
            limit = self.max_similar_tickets
        
        # Search in vector store
        results = self.tickets_collection.query(
            query_texts=[f"{subject} {description}"],
            n_results=limit
        )
        
        similar_tickets = []
        db = SessionLocal()
        
        try:
            for i, ticket_id in enumerate(results['ids'][0]):
                if ticket_id.startswith('ticket_'):
                    db_ticket_id = int(ticket_id.replace('ticket_', ''))
                    db_ticket = db.query(DBTicket).filter(DBTicket.id == db_ticket_id).first()
                    
                    if db_ticket:
                        similar_tickets.append(SimilarTicket(
                            ticket_id=db_ticket.id,
                            subject=db_ticket.subject,
                            description=db_ticket.description,
                            similarity_score=results['distances'][0][i],
                            resolution=db_ticket.resolution,
                            category=db_ticket.category.value if db_ticket.category else None
                        ))
        finally:
            db.close()
        
        return similar_tickets
    
    def generate_response(self, subject: str, description: str, category: TicketCategory, similar_tickets: List[SimilarTicket]) -> AutoResponse:
        """Generate automated response using RAG"""
        
        # Get relevant knowledge base entries
        knowledge_results = self.knowledge_collection.query(
            query_texts=[f"{subject} {description}"],
            n_results=3
        )
        
        # Build context from similar tickets
        similar_context = ""
        if similar_tickets:
            similar_context = "\n\nSimilar resolved tickets:\n"
            for ticket in similar_tickets[:3]:  # Top 3 similar tickets
                similar_context += f"- {ticket.subject}: {ticket.resolution or 'No resolution recorded'}\n"
        
        # Build knowledge base context
        knowledge_context = ""
        knowledge_references = []
        if knowledge_results['documents']:
            knowledge_context = "\n\nRelevant knowledge base information:\n"
            for i, doc in enumerate(knowledge_results['documents'][0]):
                knowledge_context += f"- {doc}\n"
                if knowledge_results['metadatas'][0][i]:
                    knowledge_references.append(knowledge_results['metadatas'][0][i]['title'])
        
        # Generate response
        prompt = f"""
        You are a customer support agent. Generate a helpful, professional response to this customer ticket.
        
        Customer Ticket:
        Subject: {subject}
        Description: {description}
        Category: {category.value}
        
        {similar_context}
        {knowledge_context}
        
        Guidelines:
        - Be empathetic and professional
        - Provide specific, actionable solutions
        - Reference relevant policies or procedures
        - Keep the response concise but comprehensive
        - If escalation is needed, mention that a specialist will contact them
        
        Generate a response that addresses the customer's concern:
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Calculate confidence based on similarity scores and knowledge base relevance
            avg_similarity = np.mean([t.similarity_score for t in similar_tickets]) if similar_tickets else 0
            knowledge_relevance = len(knowledge_references) / 3  # Normalize to 0-1
            confidence_score = (avg_similarity + knowledge_relevance) / 2
            
            # Determine if escalation is suggested
            suggested_escalation = confidence_score < self.confidence_threshold
            
            return AutoResponse(
                response_text=response_text,
                confidence_score=confidence_score,
                similar_tickets=similar_tickets,
                knowledge_base_references=knowledge_references,
                suggested_escalation=suggested_escalation
            )
            
        except Exception as e:
            print(f"Error in response generation: {e}")
            return AutoResponse(
                response_text="Thank you for contacting us. We have received your request and will get back to you shortly.",
                confidence_score=0.0,
                similar_tickets=similar_tickets,
                knowledge_base_references=knowledge_references,
                suggested_escalation=True
            )
    
    def add_ticket_to_vector_store(self, ticket_id: int, subject: str, description: str, category: str):
        """Add a new ticket to the vector store for future similarity searches"""
        
        self.tickets_collection.add(
            documents=[f"{subject} {description}"],
            metadatas=[{"ticket_id": ticket_id, "category": category}],
            ids=[f"ticket_{ticket_id}"]
        )
    
    def get_ticket_statistics(self) -> Dict[str, Any]:
        """Get statistics about tickets in the system"""
        
        db = SessionLocal()
        try:
            total_tickets = db.query(DBTicket).count()
            open_tickets = db.query(DBTicket).filter(DBTicket.status == "open").count()
            
            # Category distribution
            category_counts = {}
            for category in TicketCategory:
                count = db.query(DBTicket).filter(DBTicket.category == category).count()
                category_counts[category.value] = count
            
            # Priority distribution
            priority_counts = {}
            for priority in TicketPriority:
                count = db.query(DBTicket).filter(DBTicket.priority == priority).count()
                priority_counts[priority.value] = count
            
            return {
                "total_tickets": total_tickets,
                "open_tickets": open_tickets,
                "category_distribution": category_counts,
                "priority_distribution": priority_counts
            }
        finally:
            db.close() 