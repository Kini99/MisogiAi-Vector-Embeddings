import os
import PyPDF2
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import logging
from config import config
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.chroma_client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection("documents")
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def calculate_metadata(self, chunk: str, chunk_index: int, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metadata for a text chunk"""
        return {
            "chunk_index": chunk_index,
            "chunk_size": len(chunk),
            "word_count": len(chunk.split()),
            "document_title": document_info.get("title", ""),
            "document_filename": document_info.get("filename", ""),
            "processed_at": datetime.utcnow().isoformat(),
            "chunk_hash": hashlib.md5(chunk.encode()).hexdigest()
        }
    
    def store_in_vector_db(self, chunks: List[str], embeddings: List[List[float]], 
                          metadata_list: List[Dict[str, Any]], document_id: str) -> List[str]:
        """Store chunks in ChromaDB vector database"""
        try:
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Add to ChromaDB collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadata_list,
                ids=ids
            )
            
            logger.info(f"Stored {len(chunks)} chunks in vector database for document {document_id}")
            return ids
            
        except Exception as e:
            logger.error(f"Error storing in vector database: {e}")
            raise
    
    def process_document(self, file_path: str, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process a document: extract text, chunk, embed, and store"""
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Extract text
            text = self.extract_text_from_pdf(file_path)
            if not text.strip():
                raise ValueError("No text extracted from document")
            
            # Chunk text
            chunks = self.chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            # Generate metadata for each chunk
            metadata_list = []
            for i, chunk in enumerate(chunks):
                metadata = self.calculate_metadata(chunk, i, document_info)
                metadata_list.append(metadata)
            
            # Store in vector database
            document_id = str(document_info.get("id", hashlib.md5(file_path.encode()).hexdigest()))
            chunk_ids = self.store_in_vector_db(chunks, embeddings, metadata_list, document_id)
            
            # Generate summary
            summary = self.generate_summary(text)
            
            return {
                "document_id": document_id,
                "chunks": chunks,
                "embeddings": embeddings,
                "metadata_list": metadata_list,
                "chunk_ids": chunk_ids,
                "summary": summary,
                "total_chunks": len(chunks),
                "total_words": len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a summary of the document text"""
        try:
            # Simple extractive summarization - take first few sentences
            sentences = text.split('.')
            summary_sentences = sentences[:3]  # Take first 3 sentences
            summary = '. '.join(summary_sentences) + '.'
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def search_documents(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search documents using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'id': results['ids'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks from vector database"""
        try:
            # Get all chunks for this document
            results = self.collection.get(
                where={"document_filename": {"$contains": document_id}}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False 