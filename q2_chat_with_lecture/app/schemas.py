from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Lecture schemas
class LectureBase(BaseModel):
    title: str = Field(..., description="Title of the lecture")
    filename: str = Field(..., description="Original filename")

class LectureCreate(LectureBase):
    pass

class LectureResponse(LectureBase):
    id: int
    file_path: str
    duration: Optional[float] = None
    file_size: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Transcript schemas
class TranscriptResponse(BaseModel):
    id: int
    lecture_id: int
    content: str
    language: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessageBase(BaseModel):
    content: str = Field(..., description="Message content")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    chat_session_id: int
    role: str
    timestamp_references: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    session_name: str = Field(..., description="Name of the chat session")

class ChatSessionCreate(ChatSessionBase):
    lecture_id: int

class ChatSessionResponse(ChatSessionBase):
    id: int
    lecture_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True

# Chat response schemas
class ChatResponse(BaseModel):
    response: str
    timestamp_references: List[str] = []
    sources: List[Dict[str, Any]] = []
    confidence: Optional[float] = None
    error: Optional[str] = None

class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question about the lecture")
    chat_session_id: Optional[int] = None

# Summary schemas
class SummaryRequest(BaseModel):
    time_range: Optional[str] = Field(None, description="Time range in format 'start-end' (seconds)")

class SummaryResponse(BaseModel):
    summary: str
    key_points: List[str] = []
    duration: str
    chunks_used: int
    error: Optional[str] = None

# Upload response
class UploadResponse(BaseModel):
    lecture_id: int
    message: str
    status: str

# Error response
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None 