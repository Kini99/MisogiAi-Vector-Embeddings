import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from config import config
from document_processor import DocumentProcessor
from web_search import WebSearchEngine
import asyncio
import time  # Add this import at the top

logger = logging.getLogger(__name__)

class HybridSearchEngine:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.web_search_engine = WebSearchEngine()
        
        # Dense retrieval model
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Sparse retrieval model
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Re-ranking model
        self.cross_encoder = CrossEncoder(config.RERANK_MODEL)
        
        # Store TF-IDF matrix for documents
        self.document_texts = []
        self.tfidf_matrix = None
        self.tfidf_fitted = False
        
    def fit_tfidf(self, documents: List[str]):
        """Fit TF-IDF vectorizer on document collection"""
        try:
            self.document_texts = documents
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            self.tfidf_fitted = True
            logger.info(f"TF-IDF fitted on {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error fitting TF-IDF: {e}")
            raise
    
    def dense_retrieval(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Perform dense retrieval using embeddings"""
        try:
            # Search in document vector store
            doc_results = self.document_processor.search_documents(query, n_results)
            
            # Convert to standard format
            dense_results = []
            for result in doc_results:
                dense_results.append({
                    'content': result['content'],
                    'title': result['metadata'].get('document_title', ''),
                    'url': None,
                    'source_type': 'document',
                    'relevance_score': 1.0 - result['distance'],  # Convert distance to similarity
                    'credibility_score': 0.8,  # Documents are generally credible
                    'metadata': result['metadata'],
                    'id': result['id']
                })
            
            return dense_results
            
        except Exception as e:
            logger.error(f"Error in dense retrieval: {e}")
            return []
    
    def sparse_retrieval(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Perform sparse retrieval using TF-IDF"""
        try:
            if not self.tfidf_fitted:
                logger.warning("TF-IDF not fitted, returning empty results")
                return []
            
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:n_results]
            
            sparse_results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include relevant results
                    sparse_results.append({
                        'content': self.document_texts[idx],
                        'title': f"Document {idx}",
                        'url': None,
                        'source_type': 'document',
                        'relevance_score': float(similarities[idx]),
                        'credibility_score': 0.8,
                        'metadata': {'chunk_index': idx},
                        'id': f"sparse_{idx}"
                    })
            
            return sparse_results
            
        except Exception as e:
            logger.error(f"Error in sparse retrieval: {e}")
            return []
    
    def combine_results(self, dense_results: List[Dict], sparse_results: List[Dict],
                       dense_weight: float = 0.7, sparse_weight: float = 0.3) -> List[Dict]:
        """Combine dense and sparse results using weighted scoring"""
        try:
            # Create a mapping of content to results for deduplication
            content_map = {}
            
            # Process dense results
            for result in dense_results:
                content_key = result['content'][:100]  # Use first 100 chars as key
                if content_key not in content_map:
                    content_map[content_key] = {
                        **result,
                        'dense_score': result['relevance_score'],
                        'sparse_score': 0.0,
                        'combined_score': result['relevance_score'] * dense_weight
                    }
            
            # Process sparse results
            for result in sparse_results:
                content_key = result['content'][:100]
                if content_key in content_map:
                    # Update existing result
                    content_map[content_key]['sparse_score'] = result['relevance_score']
                    content_map[content_key]['combined_score'] += result['relevance_score'] * sparse_weight
                else:
                    # Add new result
                    content_map[content_key] = {
                        **result,
                        'dense_score': 0.0,
                        'sparse_score': result['relevance_score'],
                        'combined_score': result['relevance_score'] * sparse_weight
                    }
            
            # Convert to list and sort by combined score
            combined_results = list(content_map.values())
            combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Error combining results: {e}")
            return dense_results + sparse_results
    
    def re_rank_results(self, query: str, results: List[Dict], top_k: int = 10) -> List[Dict]:
        """Re-rank results using cross-encoder"""
        try:
            if not results:
                return results
            
            # Prepare pairs for cross-encoder
            pairs = []
            for result in results:
                pairs.append([query, result['content']])
            
            # Get cross-encoder scores
            if pairs:
                scores = self.cross_encoder.predict(pairs)
                
                # Update results with re-ranking scores
                for i, result in enumerate(results):
                    result['rerank_score'] = float(scores[i])
                    result['final_score'] = (result['combined_score'] * 0.7) + (result['rerank_score'] * 0.3)
            else:
                for result in results:
                    result['rerank_score'] = 0.0
                    result['final_score'] = result['combined_score']
            
            # Sort by final score
            results.sort(key=lambda x: x['final_score'], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in re-ranking: {e}")
            return results[:top_k]
    
    async def hybrid_search(self, query: str, max_results: int = 10,
                          dense_weight: float = 0.7, sparse_weight: float = 0.3,
                          include_web: bool = True) -> Dict[str, Any]:
        """Perform hybrid search combining document and web results"""
        try:
            start_time = time.time()
            
            # Document search (dense + sparse)
            dense_results = self.dense_retrieval(query, max_results)
            sparse_results = self.sparse_retrieval(query, max_results)
            
            # Combine document results
            doc_results = self.combine_results(
                dense_results, sparse_results, dense_weight, sparse_weight
            )
            
            # Re-rank document results
            doc_results = self.re_rank_results(query, doc_results, max_results)
            
            # Web search (if enabled)
            web_results = []
            if include_web:
                web_results = await self.web_search_engine.search_web(query, max_results)
                
                # Convert web results to standard format
                web_results_formatted = []
                for result in web_results:
                    web_results_formatted.append({
                        'content': result.get('content', result['snippet']),
                        'title': result['title'],
                        'url': result['url'],
                        'source_type': 'web',
                        'relevance_score': result['relevance_score'],
                        'credibility_score': result['credibility_score'],
                        'metadata': {
                            'search_engine': result['search_engine'],
                            'url': result['url']
                        },
                        'id': f"web_{hash(result['url'])}"
                    })
                
                # Combine with document results
                all_results = self.combine_results(
                    doc_results, web_results_formatted, 0.6, 0.4
                )
            else:
                all_results = doc_results
            
            # Final re-ranking
            final_results = self.re_rank_results(query, all_results, max_results)
            
            response_time = time.time() - start_time
            
            return {
                'query': query,
                'results': final_results,
                'total_results': len(final_results),
                'document_results': len(doc_results),
                'web_results': len(web_results) if include_web else 0,
                'response_time': response_time,
                'search_type': 'hybrid'
            }
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return {
                'query': query,
                'results': [],
                'total_results': 0,
                'document_results': 0,
                'web_results': 0,
                'response_time': 0,
                'search_type': 'hybrid',
                'error': str(e)
            }
    
    def search_documents_only(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search only in uploaded documents"""
        try:
            start_time = time.time()
            
            dense_results = self.dense_retrieval(query, max_results)
            sparse_results = self.sparse_retrieval(query, max_results)
            
            combined_results = self.combine_results(dense_results, sparse_results)
            final_results = self.re_rank_results(query, combined_results, max_results)
            
            response_time = time.time() - start_time
            
            return {
                'query': query,
                'results': final_results,
                'total_results': len(final_results),
                'response_time': response_time,
                'search_type': 'document'
            }
            
        except Exception as e:
            logger.error(f"Error in document search: {e}")
            return {
                'query': query,
                'results': [],
                'total_results': 0,
                'response_time': 0,
                'search_type': 'document',
                'error': str(e)
            }
    
    async def search_web_only(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search only on the web"""
        try:
            start_time = time.time()
            
            web_results = await self.web_search_engine.search_web(query, max_results)
            
            # Convert to standard format
            formatted_results = []
            for result in web_results:
                formatted_results.append({
                    'content': result.get('content', result['snippet']),
                    'title': result['title'],
                    'url': result['url'],
                    'source_type': 'web',
                    'relevance_score': result['relevance_score'],
                    'credibility_score': result['credibility_score'],
                    'metadata': {
                        'search_engine': result['search_engine'],
                        'url': result['url']
                    },
                    'id': f"web_{hash(result['url'])}"
                })
            
            response_time = time.time() - start_time
            
            return {
                'query': query,
                'results': formatted_results,
                'total_results': len(formatted_results),
                'response_time': response_time,
                'search_type': 'web'
            }
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {
                'query': query,
                'results': [],
                'total_results': 0,
                'response_time': 0,
                'search_type': 'web',
                'error': str(e)
            } 