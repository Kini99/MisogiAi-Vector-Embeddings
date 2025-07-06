import google.generativeai as genai
from typing import List, Dict, Any, Optional
import logging
from config import config
from hybrid_search import HybridSearchEngine
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize search engine
        self.search_engine = HybridSearchEngine()
        
        # System prompts for different tasks
        self.system_prompts = {
            'research': """You are an advanced research assistant. Your task is to synthesize information from multiple sources to provide comprehensive, accurate, and well-cited responses.

Key responsibilities:
1. Analyze and synthesize information from provided sources
2. Provide accurate citations and source attribution
3. Distinguish between facts, opinions, and uncertainties
4. Present information in a clear, organized manner
5. Highlight conflicting information when present
6. Suggest areas for further research when appropriate

Guidelines:
- Always cite your sources using the provided metadata
- Be transparent about limitations and uncertainties
- Present multiple perspectives when available
- Use clear, academic writing style
- Structure responses logically with headings when appropriate""",
            
            'qa': """You are a helpful question-answering assistant. Answer questions based on the provided context and sources.

Guidelines:
- Answer directly and concisely
- Cite sources for factual claims
- If information is not available in the sources, say so
- Be helpful and informative""",
            
            'summary': """You are a summarization expert. Create comprehensive summaries of the provided content.

Guidelines:
- Capture key points and main ideas
- Maintain factual accuracy
- Include important details and context
- Use clear, organized structure
- Highlight key findings or conclusions"""
        }
    
    def format_sources(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for inclusion in prompt"""
        if not results:
            return "No sources available."
        
        formatted_sources = []
        for i, result in enumerate(results, 1):
            source_info = f"Source {i}:\n"
            
            if result.get('title'):
                source_info += f"Title: {result['title']}\n"
            
            if result.get('url'):
                source_info += f"URL: {result['url']}\n"
            
            if result.get('source_type'):
                source_info += f"Type: {result['source_type']}\n"
            
            if result.get('credibility_score'):
                source_info += f"Credibility: {result['credibility_score']:.2f}\n"
            
            source_info += f"Content: {result['content'][:1000]}...\n"
            source_info += "-" * 50
            
            formatted_sources.append(source_info)
        
        return "\n\n".join(formatted_sources)
    
    def create_prompt(self, query: str, sources: List[Dict[str, Any]], 
                     task_type: str = 'research') -> str:
        """Create a prompt for the LLM"""
        system_prompt = self.system_prompts.get(task_type, self.system_prompts['research'])
        
        formatted_sources = self.format_sources(sources)
        
        prompt = f"""{system_prompt}

Query: {query}

Sources:
{formatted_sources}

Please provide a comprehensive response based on the sources above. Include proper citations and source attribution."""

        return prompt
    
    async def generate_response(self, query: str, sources: List[Dict[str, Any]], 
                              task_type: str = 'research') -> Dict[str, Any]:
        """Generate response using Gemini 2.0 Flash"""
        try:
            start_time = time.time()
            
            # Create prompt
            prompt = self.create_prompt(query, sources, task_type)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            generation_time = time.time() - start_time
            
            return {
                'response': response.text,
                'sources': sources,
                'generation_time': generation_time,
                'model': 'gemini-2.0-flash-exp',
                'task_type': task_type,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                'response': f"Error generating response: {str(e)}",
                'sources': sources,
                'generation_time': 0,
                'model': 'gemini-2.0-flash-exp',
                'task_type': task_type,
                'query': query,
                'error': str(e)
            }
    
    async def research_query(self, query: str, max_results: int = 10,
                           search_type: str = 'hybrid') -> Dict[str, Any]:
        """Perform research query with hybrid search and response generation"""
        try:
            start_time = time.time()
            
            # Perform search
            if search_type == 'hybrid':
                search_results = await self.search_engine.hybrid_search(query, max_results)
            elif search_type == 'document':
                search_results = self.search_engine.search_documents_only(query, max_results)
            elif search_type == 'web':
                search_results = await self.search_engine.search_web_only(query, max_results)
            else:
                raise ValueError(f"Invalid search type: {search_type}")
            
            if 'error' in search_results:
                return {
                    'query': query,
                    'response': f"Search error: {search_results['error']}",
                    'sources': [],
                    'search_type': search_type,
                    'response_time': 0,
                    'error': search_results['error']
                }
            
            # Generate response
            response_data = await self.generate_response(
                query, search_results['results'], 'research'
            )
            
            total_time = time.time() - start_time
            
            return {
                'query': query,
                'response': response_data['response'],
                'sources': response_data['sources'],
                'search_type': search_type,
                'search_time': search_results['response_time'],
                'generation_time': response_data['generation_time'],
                'total_time': total_time,
                'total_results': search_results['total_results'],
                'model': response_data['model']
            }
            
        except Exception as e:
            logger.error(f"Error in research query: {e}")
            return {
                'query': query,
                'response': f"Error processing query: {str(e)}",
                'sources': [],
                'search_type': search_type,
                'response_time': 0,
                'error': str(e)
            }
    
    async def answer_question(self, question: str, context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Answer a specific question with optional context"""
        try:
            if context:
                # Use provided context
                sources = context
            else:
                # Search for relevant information
                search_results = await self.search_engine.hybrid_search(question, 5)
                sources = search_results['results']
            
            # Generate answer
            response_data = await self.generate_response(question, sources, 'qa')
            
            return {
                'question': question,
                'answer': response_data['response'],
                'sources': response_data['sources'],
                'generation_time': response_data['generation_time'],
                'model': response_data['model']
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'question': question,
                'answer': f"Error answering question: {str(e)}",
                'sources': [],
                'generation_time': 0,
                'error': str(e)
            }
    
    async def summarize_documents(self, documents: List[Dict[str, Any]], 
                                summary_type: str = 'comprehensive') -> Dict[str, Any]:
        """Generate summary of multiple documents"""
        try:
            # Create summary query based on type
            if summary_type == 'comprehensive':
                query = "Please provide a comprehensive summary of the following documents, highlighting key themes, findings, and relationships between the sources."
            elif summary_type == 'executive':
                query = "Please provide an executive summary of the following documents, focusing on main points and key insights."
            else:
                query = f"Please provide a {summary_type} summary of the following documents."
            
            # Generate summary
            response_data = await self.generate_response(query, documents, 'summary')
            
            return {
                'summary_type': summary_type,
                'summary': response_data['response'],
                'sources': response_data['sources'],
                'generation_time': response_data['generation_time'],
                'model': response_data['model']
            }
            
        except Exception as e:
            logger.error(f"Error summarizing documents: {e}")
            return {
                'summary_type': summary_type,
                'summary': f"Error generating summary: {str(e)}",
                'sources': documents,
                'generation_time': 0,
                'error': str(e)
            }
    
    def extract_citations(self, response: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and validate citations from response"""
        citations = []
        
        for i, source in enumerate(sources, 1):
            # Check if source is mentioned in response
            source_mentioned = False
            if source.get('title') and source['title'].lower() in response.lower():
                source_mentioned = True
            elif source.get('url') and source['url'] in response:
                source_mentioned = True
            
            citation = {
                'source_index': i,
                'title': source.get('title', ''),
                'url': source.get('url', ''),
                'source_type': source.get('source_type', ''),
                'credibility_score': source.get('credibility_score', 0),
                'mentioned_in_response': source_mentioned
            }
            citations.append(citation)
        
        return citations
    
    async def fact_check_response(self, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic fact checking of generated response"""
        try:
            fact_check_prompt = f"""Please fact-check the following response against the provided sources. 
            Identify any claims that are not supported by the sources or that contradict the sources.

            Response to check:
            {response}

            Sources:
            {self.format_sources(sources)}

            Please provide:
            1. A confidence score (0-1) for the factual accuracy
            2. Any unsupported claims
            3. Any contradictions with sources
            4. Overall assessment"""

            fact_check_response = self.model.generate_content(fact_check_prompt)
            
            return {
                'fact_check_result': fact_check_response.text,
                'response_length': len(response),
                'source_count': len(sources),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fact checking: {e}")
            return {
                'fact_check_result': f"Error performing fact check: {str(e)}",
                'error': str(e)
            } 