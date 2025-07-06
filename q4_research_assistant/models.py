from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("UserSession", back_populates="user")
    documents = relationship("Document", back_populates="user")
    searches = relationship("SearchHistory", back_populates="user")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="sessions")
    queries = relationship("SearchHistory", back_populates="session")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_type = Column(String(50))
    title = Column(String(255))
    content = Column(Text)
    summary = Column(Text)
    embedding_id = Column(String(255))  # Reference to vector store
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    is_processed = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Text)  # JSON string of embedding vector
    metadata = Column(Text)  # JSON string of metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("user_sessions.id"))
    query = Column(Text)
    response = Column(Text)
    sources = Column(Text)  # JSON string of sources
    search_type = Column(String(50))  # 'document', 'web', 'hybrid'
    response_time = Column(Float)  # in seconds
    user_rating = Column(Integer)  # 1-5 rating
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="searches")
    session = relationship("UserSession", back_populates="queries")

class WebSearchResult(Base):
    __tablename__ = "web_search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text)
    title = Column(String(500))
    url = Column(String(1000))
    snippet = Column(Text)
    content = Column(Text)
    credibility_score = Column(Float)
    relevance_score = Column(Float)
    search_engine = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class ResponseQuality(Base):
    __tablename__ = "response_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    search_history_id = Column(Integer, ForeignKey("search_history.id"))
    relevance_score = Column(Float)
    accuracy_score = Column(Float)
    completeness_score = Column(Float)
    coherence_score = Column(Float)
    overall_score = Column(Float)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow) 