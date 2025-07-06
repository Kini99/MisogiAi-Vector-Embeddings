import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Lecture, ChatSession, ChatMessage
from app.schemas import (
    ChatRequest, ChatResponse, ChatSessionCreate, ChatSessionResponse,
    ChatMessageResponse, SummaryRequest, SummaryResponse
)
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session for a lecture"""
    
    # Verify lecture exists
    lecture = db.query(Lecture).filter(Lecture.id == session_data.lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    # Check if lecture is processed
    if lecture.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail="Lecture is not ready for chat. Please wait for processing to complete."
        )
    
    # Create chat session
    chat_session = ChatSession(
        lecture_id=session_data.lecture_id,
        session_name=session_data.session_name
    )
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    
    return chat_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    lecture_id: int = None,
    db: Session = Depends(get_db)
):
    """Get chat sessions, optionally filtered by lecture"""
    query = db.query(ChatSession)
    if lecture_id:
        query = query.filter(ChatSession.lecture_id == lecture_id)
    
    sessions = query.order_by(ChatSession.updated_at.desc()).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific chat session with messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: int,
    message_data: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a message in a chat session"""
    
    # Get chat session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Verify lecture is ready
    lecture = db.query(Lecture).filter(Lecture.id == session.lecture_id).first()
    if lecture.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Lecture is not ready for chat. Please wait for processing to complete."
        )
    
    try:
        # Initialize chat service
        chat_service = ChatService()
        
        # Load lecture context
        if not chat_service.load_lecture_context(session.lecture_id):
            raise HTTPException(
                status_code=500,
                detail="Failed to load lecture context"
            )
        
        # Save user message
        user_message = ChatMessage(
            chat_session_id=session_id,
            role="user",
            content=message_data.question
        )
        db.add(user_message)
        db.commit()
        
        # Generate response
        response_data = chat_service.generate_response(
            message_data.question,
            session.lecture_id
        )
        
        # Save assistant message
        assistant_message = ChatMessage(
            chat_session_id=session_id,
            role="assistant",
            content=response_data["response"],
            timestamp_references=json.dumps(response_data.get("timestamp_references", []))
        )
        db.add(assistant_message)
        db.commit()
        
        # Update session timestamp
        session.updated_at = db.query(ChatSession.updated_at).filter(
            ChatSession.id == session_id
        ).scalar()
        db.commit()
        
        return ChatResponse(
            response=response_data["response"],
            timestamp_references=response_data.get("timestamp_references", []),
            sources=response_data.get("sources", []),
            confidence=response_data.get("confidence"),
            error=response_data.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages in a chat session"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/sessions/{session_id}/summary", response_model=SummaryResponse)
async def generate_summary(
    session_id: int,
    summary_request: SummaryRequest,
    db: Session = Depends(get_db)
):
    """Generate a summary of the lecture"""
    
    # Get chat session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Verify lecture is ready
    lecture = db.query(Lecture).filter(Lecture.id == session.lecture_id).first()
    if lecture.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Lecture is not ready. Please wait for processing to complete."
        )
    
    try:
        # Initialize chat service
        chat_service = ChatService()
        
        # Load lecture context
        if not chat_service.load_lecture_context(session.lecture_id):
            raise HTTPException(
                status_code=500,
                detail="Failed to load lecture context"
            )
        
        # Generate summary
        summary_data = chat_service.summarize_lecture(
            session.lecture_id,
            summary_request.time_range
        )
        
        return SummaryResponse(
            summary=summary_data["summary"],
            key_points=summary_data.get("key_points", []),
            duration=summary_data.get("duration", "0:00"),
            chunks_used=summary_data.get("chunks_used", 0),
            error=summary_data.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Delete session (messages will be deleted due to cascade)
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.post("/quick-chat", response_model=ChatResponse)
async def quick_chat(
    lecture_id: int,
    message_data: ChatRequest,
    db: Session = Depends(get_db)
):
    """Quick chat without creating a session"""
    
    # Verify lecture exists and is ready
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    if lecture.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Lecture is not ready for chat. Please wait for processing to complete."
        )
    
    try:
        # Initialize chat service
        chat_service = ChatService()
        
        # Load lecture context
        if not chat_service.load_lecture_context(lecture_id):
            raise HTTPException(
                status_code=500,
                detail="Failed to load lecture context"
            )
        
        # Generate response
        response_data = chat_service.generate_response(
            message_data.question,
            lecture_id
        )
        
        return ChatResponse(
            response=response_data["response"],
            timestamp_references=response_data.get("timestamp_references", []),
            sources=response_data.get("sources", []),
            confidence=response_data.get("confidence"),
            error=response_data.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}") 