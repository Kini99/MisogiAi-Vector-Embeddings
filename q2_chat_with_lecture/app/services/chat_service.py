import json
from typing import List, Dict, Any, Optional
from app.services.rag_pipeline import RAGPipeline
from app.config import settings

class ChatService:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        
    def load_lecture_context(self, lecture_id: int, collection_name: str = None):
        """Load vector store for a specific lecture"""
        try:
            if collection_name:
                self.rag_pipeline.load_vector_store(collection_name)
            else:
                self.rag_pipeline.load_vector_store(f"lecture_{lecture_id}")
            return True
        except Exception as e:
            print(f"Error loading lecture context: {str(e)}")
            return False
    
    def generate_response(self, question: str, lecture_id: int, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate response using RAG pipeline (simplified)"""
        try:
            # Retrieve relevant chunks
            relevant_chunks = self.rag_pipeline.retrieve_relevant_chunks(
                question, 
                k=5, 
                lecture_id=lecture_id
            )
            
            if not relevant_chunks:
                return {
                    "response": "I couldn't find relevant information in the lecture to answer your question. Could you please rephrase or ask about a different topic?",
                    "timestamp_references": [],
                    "sources": []
                }
            
            # Prepare context from chunks
            context_parts = []
            for chunk in relevant_chunks:
                timestamp = self._format_timestamp(chunk['start_time'])
                context_parts.append(f"[{timestamp}] {chunk['content']}")
            
            context = "\n\n".join(context_parts)
            
            # Simple response generation (placeholder for OpenAI integration)
            response_text = f"Based on the lecture content, here's what I found:\n\n{context}\n\nThis information should help answer your question: {question}"
            
            # Extract timestamp references
            timestamp_references = self.rag_pipeline.format_timestamp_references(relevant_chunks)
            
            # Prepare sources for response
            sources = []
            for chunk in relevant_chunks:
                sources.append({
                    'content': chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                    'timestamp': self._format_timestamp(chunk['start_time']),
                    'start_time': chunk['start_time']
                })
            
            return {
                "response": response_text,
                "timestamp_references": timestamp_references,
                "sources": sources,
                "confidence": self._calculate_confidence(relevant_chunks, question)
            }
            
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error while processing your question: {str(e)}",
                "timestamp_references": [],
                "sources": [],
                "error": str(e)
            }
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def _calculate_confidence(self, chunks: List[Dict], question: str) -> float:
        """Calculate confidence score based on relevance"""
        # Simple confidence calculation based on number of relevant chunks
        if not chunks:
            return 0.0
        
        # Higher confidence if we have more relevant chunks
        base_confidence = min(len(chunks) / 5.0, 1.0)
        
        # Boost confidence if question contains time-related keywords
        time_keywords = ['minute', 'time', 'when', 'timestamp', 'start', 'end']
        if any(keyword in question.lower() for keyword in time_keywords):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def summarize_lecture(self, lecture_id: int, time_range: Optional[str] = None) -> Dict[str, Any]:
        """Generate lecture summary (simplified)"""
        try:
            # Retrieve chunks for summary
            if time_range:
                # Parse time range (e.g., "0-3600" for first hour)
                start_time, end_time = map(float, time_range.split('-'))
                chunks = self._get_chunks_in_time_range(lecture_id, start_time, end_time)
            else:
                chunks = self.rag_pipeline.retrieve_relevant_chunks(
                    "lecture summary key points main concepts", 
                    k=10, 
                    lecture_id=lecture_id
                )
            
            if not chunks:
                return {
                    "summary": "No content available for summarization.",
                    "key_points": [],
                    "duration": "0:00"
                }
            
            # Prepare context for summary
            context = "\n\n".join([chunk['content'] for chunk in chunks])
            
            # Simple summary generation
            summary = f"Lecture Summary:\n\nThis lecture covers various topics including:\n{context[:500]}...\n\nKey points and main concepts are discussed throughout the presentation."
            
            # Calculate total duration
            total_duration = sum(chunk['end_time'] - chunk['start_time'] for chunk in chunks)
            duration_str = self._format_timestamp(total_duration)
            
            return {
                "summary": summary,
                "key_points": self._extract_key_points(summary),
                "duration": duration_str,
                "chunks_used": len(chunks)
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "key_points": [],
                "duration": "0:00",
                "error": str(e)
            }
    
    def _get_chunks_in_time_range(self, lecture_id: int, start_time: float, end_time: float) -> List[Dict]:
        """Get chunks within a specific time range"""
        # This would need to be implemented based on your vector store capabilities
        # For now, we'll use the general retrieval
        return self.rag_pipeline.retrieve_relevant_chunks(
            "content", 
            k=20, 
            lecture_id=lecture_id
        )
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """Extract key points from summary"""
        # Simple extraction - in production, you might use more sophisticated parsing
        lines = summary.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.')):
                key_points.append(line)
        
        return key_points[:10]  # Limit to 10 key points 