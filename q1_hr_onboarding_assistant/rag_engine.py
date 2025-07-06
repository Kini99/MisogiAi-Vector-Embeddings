from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI
import json
import re
import tiktoken

class RAGEngine:
    def __init__(self, config, vector_store):
        self.config = config
        self.vector_store = vector_store
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # HR-specific query categories
        self.query_categories = {
            "leave_policy": ["vacation", "leave", "holiday", "time off", "sick", "parental", "maternity", "paternity"],
            "benefits": ["health", "insurance", "medical", "dental", "vision", "benefits", "coverage"],
            "conduct": ["conduct", "behavior", "ethics", "discipline", "code of conduct", "policies"],
            "compensation": ["salary", "compensation", "pay", "bonus", "raise", "promotion"],
            "work_arrangement": ["remote", "work from home", "telecommute", "hybrid", "office"],
            "general": ["general", "policy", "procedure", "guideline"]
        }
    
    def classify_query(self, query: str) -> str:
        """Classify the query into HR categories"""
        query_lower = query.lower()
        
        for category, keywords in self.query_categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return "general"
    
    def retrieve_relevant_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for the query"""
        # First try category-specific search
        category = self.classify_query(query)
        category_results = self.vector_store.search_by_category(query, category, n_results)
        
        # If not enough results, do general search
        if len(category_results) < 3:
            general_results = self.vector_store.search(query, n_results)
            # Combine and deduplicate results
            all_results = category_results + general_results
            seen_hashes = set()
            unique_results = []
            
            for result in all_results:
                result_hash = hash(result["text"])
                if result_hash not in seen_hashes:
                    seen_hashes.add(result_hash)
                    unique_results.append(result)
            
            return unique_results[:n_results]
        
        return category_results
    
    def generate_response(self, query: str, context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a response using OpenAI with context and citations"""
        if not context_documents:
            return {
                "answer": "I don't have enough information to answer your question. Please contact HR for assistance.",
                "sources": [],
                "confidence": "low"
            }
        
        # Prepare context with citations
        context_parts = []
        sources = []
        
        for i, doc in enumerate(context_documents):
            context_parts.append(f"[Source {i+1}]: {doc['text']}")
            sources.append({
                "document_name": doc["metadata"].get("document_name", "Unknown"),
                "section_title": doc["metadata"].get("section_title", "Unknown Section"),
                "content_type": doc["metadata"].get("content_type", "general"),
                "text_preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
            })
        
        context = "\n\n".join(context_parts)
        
        # Create system prompt
        system_prompt = """You are an HR assistant helping new employees with their onboarding questions. 
        Use the provided context to answer questions accurately and professionally.
        
        Guidelines:
        1. Only answer based on the provided context
        2. If information is not in the context, say so and suggest contacting HR
        3. Be clear and concise
        4. Use professional but friendly tone
        5. Always cite your sources using [Source X] format
        6. If the query is about specific policies, provide step-by-step instructions when possible
        
        Context:
        {context}
        """
        
        # Create user prompt
        user_prompt = f"Question: {query}\n\nPlease provide a comprehensive answer based on the context above."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt.format(context=context)},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Extract confidence based on response characteristics
            confidence = self._assess_confidence(answer, context_documents)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "query_category": self.classify_query(query)
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your request. Please try again or contact HR for assistance.",
                "sources": [],
                "confidence": "low"
            }
    
    def _assess_confidence(self, answer: str, context_documents: List[Dict[str, Any]]) -> str:
        """Assess confidence level based on answer characteristics"""
        # Check if answer contains source citations
        has_citations = bool(re.search(r'\[Source \d+\]', answer))
        
        # Check if answer is comprehensive
        answer_length = len(answer)
        
        # Check if answer contains uncertainty indicators
        uncertainty_words = ["might", "may", "could", "possibly", "not sure", "don't know", "contact HR"]
        has_uncertainty = any(word in answer.lower() for word in uncertainty_words)
        
        if has_uncertainty or not has_citations:
            return "low"
        elif answer_length > 200 and has_citations:
            return "high"
        else:
            return "medium"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a complete query through the RAG pipeline"""
        # Classify the query
        category = self.classify_query(query)
        
        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_documents(query)
        
        # Generate response
        response = self.generate_response(query, relevant_docs)
        
        # Add query metadata
        response["query"] = query
        response["query_category"] = category
        response["retrieved_documents_count"] = len(relevant_docs)
        
        return response
    
    def get_suggested_questions(self, category: Optional[str] = None) -> List[str]:
        """Get suggested questions based on category"""
        suggestions = {
            "leave_policy": [
                "How many vacation days do I get as a new employee?",
                "What's the process for requesting parental leave?",
                "How do I request sick leave?",
                "What are the company holidays?"
            ],
            "benefits": [
                "How do I enroll in health insurance?",
                "What dental coverage is available?",
                "Are there vision benefits?",
                "What retirement benefits are offered?"
            ],
            "work_arrangement": [
                "Can I work remotely and what are the guidelines?",
                "What's the hybrid work policy?",
                "How do I request flexible work arrangements?"
            ],
            "conduct": [
                "What's the dress code policy?",
                "What are the social media guidelines?",
                "How do I report workplace issues?"
            ],
            "compensation": [
                "How often are performance reviews conducted?",
                "What's the bonus structure?",
                "How do I request a salary review?"
            ],
            "general": [
                "How do I access my employee portal?",
                "What's the onboarding process?",
                "Who should I contact for HR questions?"
            ]
        }
        
        if category and category in suggestions:
            return suggestions[category]
        else:
            # Return all suggestions
            all_suggestions = []
            for cat_suggestions in suggestions.values():
                all_suggestions.extend(cat_suggestions)
            return all_suggestions 