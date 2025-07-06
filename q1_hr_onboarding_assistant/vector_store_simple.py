import chromadb
from chromadb.config import Settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any, Optional
import os
import json

class SimpleVectorStore:
    def __init__(self, config):
        self.config = config
        
        # Use TF-IDF for embeddings instead of sentence transformers
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Store documents for TF-IDF processing
        self.documents = []
        self.document_metadata = []
        
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate TF-IDF embeddings for texts"""
        try:
            # Fit and transform the texts
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Convert to dense array and normalize
            embeddings = tfidf_matrix.toarray()
            
            # Normalize to unit vectors for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            embeddings = embeddings / norms
            
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return random embeddings as fallback
            return [[0.1] * 100 for _ in texts]
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add document chunks to the vector store"""
        try:
            texts = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            # Store documents for TF-IDF processing
            self.documents.extend(texts)
            self.document_metadata.extend(metadatas)
            
            # Generate embeddings using TF-IDF
            embeddings = self._get_embeddings(texts)
            
            # Generate unique IDs
            ids = [f"doc_{i}_{hash(chunk['metadata']['document_hash'])}" 
                   for i, chunk in enumerate(chunks)]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5, 
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        try:
            # Generate query embedding using TF-IDF
            query_embedding = self._get_embeddings([query])
            
            # Prepare where clause for filtering
            where_clause = None
            if filter_metadata:
                where_clause = filter_metadata
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def search_by_category(self, query: str, category: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for documents in a specific category"""
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"content_type": category}
        )
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from the collection"""
        try:
            results = self.collection.get()
            
            documents = []
            for i in range(len(results["documents"])):
                documents.append({
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                    "id": results["ids"][i]
                })
            
            return documents
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return []
    
    def delete_document(self, document_hash: str) -> bool:
        """Delete a specific document by its hash"""
        try:
            # Get all documents
            results = self.collection.get()
            
            # Find documents with matching hash
            ids_to_delete = []
            for i, metadata in enumerate(results["metadatas"]):
                if metadata.get("document_hash") == document_hash:
                    ids_to_delete.append(results["ids"][i])
            
            # Delete the documents
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the documents in the collection"""
        try:
            results = self.collection.get()
            
            # Count documents by category
            category_counts = {}
            document_names = set()
            
            for metadata in results["metadatas"]:
                content_type = metadata.get("content_type", "unknown")
                category_counts[content_type] = category_counts.get(content_type, 0) + 1
                
                document_name = metadata.get("document_name", "unknown")
                document_names.add(document_name)
            
            return {
                "total_documents": len(results["documents"]),
                "unique_document_files": len(document_names),
                "category_distribution": category_counts,
                "document_names": list(document_names)
            }
        except Exception as e:
            print(f"Error getting document stats: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.collection.delete()
            self.documents = []
            self.document_metadata = []
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False 