from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SearchType(str, Enum):
    DOCUMENT = "document"
    WEB = "web"
    HYBRID = "hybrid"

class DocumentUploadRequest(BaseModel):
    title: Optional[str] = Field(None, description="Document title")
    description: Optional[str] = Field(None, description="Document description")

class DocumentResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    file_size: int
    file_type: str
    is_processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    search_type: SearchType = Field(SearchType.HYBRID, description="Type of search to perform")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")
    include_sources: bool = Field(True, description="Whether to include source information")
    user_id: Optional[int] = Field(None, description="User ID for session tracking")

class SearchResult(BaseModel):
    content: str
    title: Optional[str]
    url: Optional[str]
    source_type: str  # 'document' or 'web'
    relevance_score: float
    credibility_score: Optional[float]
    metadata: Optional[Dict[str, Any]]

class SearchResponse(BaseModel):
    query: str
    response: str
    sources: List[SearchResult]
    search_type: SearchType
    response_time: float
    total_results: int

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="Web search query", min_length=1)
    max_results: int = Field(10, description="Maximum number of results")
    search_engine: str = Field("serper", description="Search engine to use")

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    content: Optional[str]
    credibility_score: Optional[float]
    relevance_score: Optional[float]
    search_engine: str

class HybridSearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    dense_weight: float = Field(0.7, description="Weight for dense retrieval")
    sparse_weight: float = Field(0.3, description="Weight for sparse retrieval")
    max_results: int = Field(10, description="Maximum number of results")
    user_id: Optional[int] = Field(None, description="User ID for session tracking")

class DocumentChunk(BaseModel):
    id: int
    chunk_index: int
    content: str
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class DocumentDetailResponse(BaseModel):
    id: int
    filename: str
    title: Optional[str]
    content: str
    summary: Optional[str]
    file_size: int
    file_type: str
    is_processed: bool
    created_at: datetime
    chunks: List[DocumentChunk]
    
    class Config:
        from_attributes = True

class UserSessionRequest(BaseModel):
    username: str = Field(..., description="Username for session")
    email: Optional[str] = Field(None, description="User email")

class UserSessionResponse(BaseModel):
    session_id: str
    user_id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    response: str
    search_type: str
    response_time: float
    user_rating: Optional[int]
    created_at: datetime
    sources: Optional[str]
    
    class Config:
        from_attributes = True

class ResponseQualityRequest(BaseModel):
    search_history_id: int
    relevance_score: float = Field(..., ge=0, le=5)
    accuracy_score: float = Field(..., ge=0, le=5)
    completeness_score: float = Field(..., ge=0, le=5)
    coherence_score: float = Field(..., ge=0, le=5)
    feedback: Optional[str] = Field(None, description="User feedback")

class ResponseQualityResponse(BaseModel):
    id: int
    search_history_id: int
    overall_score: float
    relevance_score: float
    accuracy_score: float
    completeness_score: float
    coherence_score: float
    feedback: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    database_status: str
    vector_store_status: str
    search_apis_status: str 