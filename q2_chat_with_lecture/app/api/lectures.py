import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Lecture, Transcript, TranscriptChunk
from app.schemas import LectureResponse, UploadResponse, TranscriptResponse
from app.services.video_processor import VideoProcessor
from app.services.rag_pipeline import RAGPipeline
from app.config import settings
import uuid

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_lecture(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = None,
    db: Session = Depends(get_db)
):
    """Upload a lecture video file"""
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.SUPPORTED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(settings.SUPPORTED_VIDEO_FORMATS)}"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create lecture record
        lecture = Lecture(
            title=title or file.filename,
            filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            status="uploaded"
        )
        db.add(lecture)
        db.commit()
        db.refresh(lecture)
        
        # Start background processing
        background_tasks.add_task(process_lecture_background, lecture.id, db)
        
        return UploadResponse(
            lecture_id=lecture.id,
            message="Lecture uploaded successfully. Processing started in background.",
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=List[LectureResponse])
async def get_lectures(db: Session = Depends(get_db)):
    """Get all lectures"""
    lectures = db.query(Lecture).order_by(Lecture.created_at.desc()).all()
    return lectures

@router.get("/{lecture_id}", response_model=LectureResponse)
async def get_lecture(lecture_id: int, db: Session = Depends(get_db)):
    """Get a specific lecture"""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture

@router.get("/{lecture_id}/transcript", response_model=TranscriptResponse)
async def get_lecture_transcript(lecture_id: int, db: Session = Depends(get_db)):
    """Get transcript for a lecture"""
    transcript = db.query(Transcript).filter(Transcript.lecture_id == lecture_id).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

@router.delete("/{lecture_id}")
async def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    """Delete a lecture and all associated data"""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    try:
        # Delete file
        if os.path.exists(lecture.file_path):
            os.remove(lecture.file_path)
        
        # Delete from database (cascade will handle related records)
        db.delete(lecture)
        db.commit()
        
        return {"message": "Lecture deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

def process_lecture_background(lecture_id: int, db: Session):
    """Background task to process lecture video"""
    try:
        # Get lecture
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            return
        
        # Update status
        lecture.status = "processing"
        db.commit()
        
        # Initialize processors
        video_processor = VideoProcessor()
        rag_pipeline = RAGPipeline()
        
        # Get video duration
        duration = video_processor.get_video_duration(lecture.file_path)
        lecture.duration = duration
        db.commit()
        
        # Extract audio
        audio_path = video_processor.extract_audio(lecture.file_path)
        
        # Transcribe audio
        transcript_content, processing_time, language = video_processor.transcribe_audio(audio_path)
        
        # Create transcript record
        transcript = Transcript(
            lecture_id=lecture.id,
            content=transcript_content,
            language=language,
            processing_time=processing_time
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        # Process transcript with RAG pipeline
        chunks = rag_pipeline.chunk_transcript(transcript_content, lecture.id)
        
        # Save chunks to database
        for i, chunk_data in enumerate(chunks):
            chunk = TranscriptChunk(
                transcript_id=transcript.id,
                content=chunk_data['content'],
                start_time=chunk_data['start_time'],
                end_time=chunk_data['end_time'],
                chunk_index=i
            )
            db.add(chunk)
        
        db.commit()
        
        # Create vector store
        collection_name = f"lecture_{lecture.id}"
        rag_pipeline.create_vector_store(chunks, collection_name)
        
        # Update lecture status
        lecture.status = "completed"
        db.commit()
        
        # Cleanup temporary files
        video_processor.cleanup_temp_files(audio_path)
        
    except Exception as e:
        # Update status to failed
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if lecture:
            lecture.status = "failed"
            db.commit()
        print(f"Error processing lecture {lecture_id}: {str(e)}") 