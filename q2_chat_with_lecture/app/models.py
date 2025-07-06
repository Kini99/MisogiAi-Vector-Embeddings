from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Lecture(Base):
    __tablename__ = "lectures"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    duration = Column(Float, nullable=True)  # in seconds
    file_size = Column(Integer, nullable=True)  # in bytes
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transcript = relationship("Transcript", back_populates="lecture", uselist=False)
    chat_sessions = relationship("ChatSession", back_populates="lecture")

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lecture = relationship("Lecture", back_populates="transcript")
    chunks = relationship("TranscriptChunk", back_populates="transcript")

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    content = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)  # in seconds
    end_time = Column(Float, nullable=False)  # in seconds
    chunk_index = Column(Integer, nullable=False)
    embedding_id = Column(String(255), nullable=True)  # ChromaDB document ID
    
    # Relationships
    transcript = relationship("Transcript", back_populates="chunks")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    session_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lecture = relationship("Lecture", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    timestamp_references = Column(Text, nullable=True)  # JSON array of timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages") 