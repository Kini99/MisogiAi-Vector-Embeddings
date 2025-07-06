import requests
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
import logging
from config import config
import json
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class WebSearchEngine:
    def __init__(self):
        self.serper_api_key = config.SERPER_API_KEY
        self.bing_api_key = config.BING_API_KEY
        self.session = requests.Session()
        
    def search_serper(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Serper API"""
        try:
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": max_results
            }
            
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Process organic results
            if "organic" in data:
                for result in data["organic"][:max_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "search_engine": "serper",
                        "position": result.get("position", 0)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching with Serper: {e}")
            return []
    
    def search_bing(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Bing API"""
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                "Ocp-Apim-Subscription-Key": self.bing_api_key
            }
            params = {
                "q": query,
                "count": max_results,
                "mkt": "en-US"
            }
            
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "webPages" in data and "value" in data["webPages"]:
                for result in data["webPages"]["value"][:max_results]:
                    results.append({
                        "title": result.get("name", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                        "search_engine": "bing",
                        "position": result.get("id", 0)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching with Bing: {e}")
            return []
    
    async def fetch_webpage_content(self, url: str) -> Optional[str]:
        """Fetch and extract content from a webpage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Extract text content
                        text = soup.get_text()
                        
                        # Clean up whitespace
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        return text[:5000]  # Limit content length
                    
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None
    
    def calculate_credibility_score(self, url: str, title: str, snippet: str) -> float:
        """Calculate credibility score for a search result"""
        score = 0.5  # Base score
        
        # Domain credibility factors
        domain = urlparse(url).netloc.lower()
        
        # Trusted domains
        trusted_domains = [
            'wikipedia.org', 'edu', 'gov', 'nih.gov', 'who.int', 
            'nature.com', 'science.org', 'arxiv.org', 'ieee.org',
            'acm.org', 'springer.com', 'elsevier.com', 'tandfonline.com'
        ]
        
        for trusted in trusted_domains:
            if trusted in domain:
                score += 0.3
                break
        
        # Academic/research domains
        academic_keywords = ['research', 'study', 'journal', 'paper', 'academic']
        for keyword in academic_keywords:
            if keyword in domain or keyword in title.lower():
                score += 0.1
        
        # Content quality indicators
        quality_indicators = ['study', 'research', 'analysis', 'evidence', 'data']
        for indicator in quality_indicators:
            if indicator in snippet.lower():
                score += 0.05
        
        # URL structure
        if '/pdf/' in url or '.pdf' in url:
            score += 0.1  # PDFs often contain more detailed information
        
        # Recent content (if date is available)
        current_year = time.localtime().tm_year
        if str(current_year) in url or str(current_year) in title:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_relevance_score(self, query: str, title: str, snippet: str) -> float:
        """Calculate relevance score for a search result"""
        query_terms = set(query.lower().split())
        title_terms = set(title.lower().split())
        snippet_terms = set(snippet.lower().split())
        
        # Title relevance
        title_overlap = len(query_terms.intersection(title_terms))
        title_score = title_overlap / len(query_terms) if query_terms else 0
        
        # Snippet relevance
        snippet_overlap = len(query_terms.intersection(snippet_terms))
        snippet_score = snippet_overlap / len(query_terms) if query_terms else 0
        
        # Combined score (title weighted more heavily)
        relevance_score = (title_score * 0.7) + (snippet_score * 0.3)
        
        return min(relevance_score, 1.0)
    
    async def search_web(self, query: str, max_results: int = 10, 
                        search_engine: str = "serper") -> List[Dict[str, Any]]:
        """Perform web search with content fetching and scoring"""
        try:
            # Perform search
            if search_engine == "serper":
                results = self.search_serper(query, max_results)
            elif search_engine == "bing":
                results = self.search_bing(query, max_results)
            else:
                # Combine results from multiple engines
                serper_results = self.search_serper(query, max_results // 2)
                bing_results = self.search_bing(query, max_results // 2)
                results = serper_results + bing_results
            
            # Enhance results with content and scoring
            enhanced_results = []
            for result in results[:max_results]:
                # Calculate scores
                credibility_score = self.calculate_credibility_score(
                    result["url"], result["title"], result["snippet"]
                )
                relevance_score = self.calculate_relevance_score(
                    query, result["title"], result["snippet"]
                )
                
                # Fetch content (optional, can be slow)
                content = None
                if credibility_score > 0.6:  # Only fetch content for credible sources
                    content = await self.fetch_webpage_content(result["url"])
                
                enhanced_result = {
                    **result,
                    "credibility_score": credibility_score,
                    "relevance_score": relevance_score,
                    "content": content,
                    "combined_score": (credibility_score * 0.4) + (relevance_score * 0.6)
                }
                
                enhanced_results.append(enhanced_result)
            
            # Sort by combined score
            enhanced_results.sort(key=lambda x: x["combined_score"], reverse=True)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return []
    
    def search_multiple_engines(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using multiple engines and combine results"""
        try:
            # Search with both engines
            serper_results = self.search_serper(query, max_results)
            bing_results = self.search_bing(query, max_results)
            
            # Combine and deduplicate results
            all_results = serper_results + bing_results
            seen_urls = set()
            unique_results = []
            
            for result in all_results:
                if result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    unique_results.append(result)
            
            # Sort by position and take top results
            unique_results.sort(key=lambda x: x.get("position", 999))
            return unique_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error in multiple engine search: {e}")
            return [] 