from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class QueryCategory(str, Enum):
    LEAVE_POLICY = "leave_policy"
    BENEFITS = "benefits"
    CONDUCT = "conduct"
    COMPENSATION = "compensation"
    WORK_ARRANGEMENT = "work_arrangement"
    GENERAL = "general"

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Source(BaseModel):
    document_name: str
    section_title: str
    content_type: str
    text_preview: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[Source]
    confidence: ConfidenceLevel
    query_category: QueryCategory
    retrieved_documents_count: int
    timestamp: datetime = Field(default_factory=datetime.now)

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    category_filter: Optional[QueryCategory] = None

class DocumentUploadResponse(BaseModel):
    filename: str
    status: str
    chunks_processed: int
    document_hash: str
    processing_time: float

class DocumentInfo(BaseModel):
    document_name: str
    document_hash: str
    content_type: str
    section_title: str
    processed_at: datetime
    text_preview: str

class DocumentStats(BaseModel):
    total_documents: int
    unique_document_files: int
    category_distribution: Dict[str, int]
    document_names: List[str]

class SuggestedQuestionsResponse(BaseModel):
    category: Optional[QueryCategory] = None
    questions: List[str]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    services: Dict[str, str] 