import re
import json
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings

class RAGPipeline:
    def __init__(self):
        self.vector_store = None
        self.collection_name = "lecture_chunks"
        
    def chunk_transcript(self, transcript: str, lecture_id: int) -> List[Dict[str, Any]]:
        """Chunk transcript with timestamp preservation"""
        chunks = []
        
        # Split transcript into segments based on timestamps
        segments = self._parse_transcript_segments(transcript)
        
        for segment in segments:
            # Simple chunking for now
            chunks.append({
                'content': segment['text'],
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'lecture_id': lecture_id
            })
        
        return chunks
    
    def _parse_transcript_segments(self, transcript: str) -> List[Dict[str, Any]]:
        """Parse transcript into segments with timestamps"""
        segments = []
        
        # Regex to match timestamp patterns [MM:SS - MM:SS]
        timestamp_pattern = r'\[(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\]\s*(.*?)(?=\[\d{2}:\d{2}\s*-\s*\d{2}:\d{2}\]|$)'
        
        matches = re.findall(timestamp_pattern, transcript, re.DOTALL)
        
        for match in matches:
            start_min, start_sec, end_min, end_sec, text = match
            
            start_time = int(start_min) * 60 + int(start_sec)
            end_time = int(end_min) * 60 + int(end_sec)
            
            segments.append({
                'text': text.strip(),
                'start_time': start_time,
                'end_time': end_time
            })
        
        return segments
    
    def create_vector_store(self, chunks: List[Dict[str, Any]], collection_name: str = None):
        """Create vector store from chunks (simplified)"""
        if collection_name:
            self.collection_name = collection_name
        
        # For now, just store chunks in memory
        self.chunks = chunks
        return True
    
    def load_vector_store(self, collection_name: str = None):
        """Load existing vector store (simplified)"""
        if collection_name:
            self.collection_name = collection_name
        
        # For now, just return True
        return True
    
    def retrieve_relevant_chunks(self, query: str, k: int = 5, lecture_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query (simplified)"""
        if not hasattr(self, 'chunks'):
            return []
        
        # Simple keyword matching for now
        relevant_chunks = []
        query_lower = query.lower()
        
        for chunk in self.chunks:
            if lecture_id and chunk.get('lecture_id') != lecture_id:
                continue
                
            if query_lower in chunk['content'].lower():
                relevant_chunks.append({
                    'content': chunk['content'],
                    'metadata': {
                        'start_time': chunk['start_time'],
                        'end_time': chunk['end_time'],
                        'lecture_id': chunk['lecture_id'],
                        'timestamp': f"{chunk['start_time']:.1f}-{chunk['end_time']:.1f}"
                    },
                    'start_time': chunk['start_time'],
                    'end_time': chunk['end_time'],
                    'timestamp': f"{chunk['start_time']:.1f}-{chunk['end_time']:.1f}"
                })
        
        return relevant_chunks[:k]
    
    def format_timestamp_references(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Format timestamp references for response"""
        timestamps = []
        
        for chunk in chunks:
            start_time = chunk['start_time']
            end_time = chunk['end_time']
            
            # Format as MM:SS
            start_str = f"{int(start_time // 60):02d}:{int(start_time % 60):02d}"
            end_str = f"{int(end_time // 60):02d}:{int(end_time % 60):02d}"
            
            timestamps.append(f"{start_str}-{end_str}")
        
        return timestamps
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        if not hasattr(self, 'chunks'):
            return {"error": "Vector store not initialized"}
        
        return {
            "total_documents": len(self.chunks),
            "collection_name": self.collection_name,
            "embedding_model": "simple_keyword_matching"
        } 