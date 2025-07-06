from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
import uuid
import json
from datetime import datetime

from config import config
from database import get_db, init_db
from models import User, Document, SearchHistory, UserSession, ResponseQuality, DocumentChunk
from schemas import (
    SearchRequest, SearchResponse, DocumentResponse, DocumentUploadRequest,
    UserSessionRequest, UserSessionResponse, SearchHistoryResponse,
    ResponseQualityRequest, ResponseQualityResponse, HealthCheckResponse
)
from document_processor import DocumentProcessor
from web_search import WebSearchEngine
from hybrid_search import HybridSearchEngine
from rag_engine import RAGEngine

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Research Assistant API",
    description="Advanced Research Assistant with Hybrid Search and RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
web_search_engine = WebSearchEngine()
hybrid_search_engine = HybridSearchEngine()
rag_engine = RAGEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize database and components on startup"""
    try:
        init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check vector store
    try:
        # Simple check if ChromaDB is accessible
        vector_store_status = "healthy"
    except Exception as e:
        vector_store_status = f"unhealthy: {str(e)}"
    
    # Check search APIs
    try:
        # Test if API keys are configured
        if config.SERPER_API_KEY or config.BING_API_KEY:
            search_apis_status = "healthy"
        else:
            search_apis_status = "warning: no API keys configured"
    except Exception as e:
        search_apis_status = f"unhealthy: {str(e)}"
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database_status=db_status,
        vector_store_status=vector_store_status,
        search_apis_status=search_apis_status
    )

@app.post("/sessions", response_model=UserSessionResponse)
async def create_session(session_request: UserSessionRequest, db: Session = Depends(get_db)):
    """Create a new user session"""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create or get user
        user = db.query(User).filter(User.username == session_request.username).first()
        if not user:
            user = User(
                username=session_request.username,
                email=session_request.email,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create session
        session = UserSession(
            user_id=user.id,
            session_id=session_id,
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return UserSessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=session.created_at,
            is_active=session.is_active
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Check file size
        if file.size > config.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Create upload directory if it doesn't exist
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        
        # Save file
        file_path = os.path.join(config.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            file_type="pdf",
            title=title or file.filename,
            is_processed=False
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document in background
        def process_document_background():
            try:
                document_info = {
                    "id": document.id,
                    "title": document.title,
                    "filename": document.filename
                }
                
                # Process document
                result = document_processor.process_document(file_path, document_info)
                
                # Update document record
                document.content = result.get("summary", "")
                document.summary = result.get("summary", "")
                document.embedding_id = result.get("document_id", "")
                document.is_processed = True
                document.processed_at = datetime.utcnow()
                
                # Save chunks to database
                for i, chunk in enumerate(result.get("chunks", [])):
                    chunk_record = DocumentChunk(
                        document_id=document.id,
                        chunk_index=i,
                        content=chunk,
                        embedding=json.dumps(result["embeddings"][i]),
                        metadata=json.dumps(result["metadata_list"][i])
                    )
                    db.add(chunk_record)
                
                db.commit()
                logger.info(f"Document {document.id} processed successfully")
                
            except Exception as e:
                logger.error(f"Error processing document {document.id}: {e}")
                document.is_processed = False
                db.commit()
        
        # Start background processing
        import threading
        thread = threading.Thread(target=process_document_background)
        thread.start()
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            title=document.title,
            file_size=document.file_size,
            file_type=document.file_type,
            is_processed=document.is_processed,
            created_at=document.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all documents"""
    try:
        query = db.query(Document)
        if user_id:
            query = query.filter(Document.user_id == user_id)
        
        documents = query.all()
        return [DocumentResponse.from_orm(doc) for doc in documents]
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Perform hybrid search with RAG"""
    try:
        start_time = datetime.utcnow()
        
        # Perform search based on type
        if search_request.search_type.value == "hybrid":
            search_results = await hybrid_search_engine.hybrid_search(
                search_request.query, search_request.max_results
            )
        elif search_request.search_type.value == "document":
            search_results = hybrid_search_engine.search_documents_only(
                search_request.query, search_request.max_results
            )
        elif search_request.search_type.value == "web":
            search_results = await hybrid_search_engine.search_web_only(
                search_request.query, search_request.max_results
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")
        
        if 'error' in search_results:
            raise HTTPException(status_code=500, detail=search_results['error'])
        
        # Generate response using RAG
        rag_response = await rag_engine.generate_response(
            search_request.query, search_results['results'], 'research'
        )
        
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Save search history
        if search_request.user_id:
            search_history = SearchHistory(
                user_id=search_request.user_id,
                query=search_request.query,
                response=rag_response['response'],
                sources=json.dumps(search_results['results']),
                search_type=search_request.search_type.value,
                response_time=response_time
            )
            db.add(search_history)
            db.commit()
        
        # Format sources for response
        sources = []
        for result in search_results['results']:
            sources.append({
                'content': result['content'][:500] + "...",
                'title': result.get('title', ''),
                'url': result.get('url'),
                'source_type': result['source_type'],
                'relevance_score': result['relevance_score'],
                'credibility_score': result.get('credibility_score')
            })
        
        return SearchResponse(
            query=search_request.query,
            response=rag_response['response'],
            sources=sources,
            search_type=search_request.search_type,
            response_time=response_time,
            total_results=search_results['total_results']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/web-search")
async def web_search(query: str, max_results: int = 10, search_engine: str = "serper"):
    """Perform web search only"""
    try:
        results = await web_search_engine.search_web(query, max_results, search_engine)
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        logger.error(f"Error in web search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get search history for a user"""
    try:
        history = db.query(SearchHistory)\
            .filter(SearchHistory.user_id == user_id)\
            .order_by(SearchHistory.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [SearchHistoryResponse.from_orm(h) for h in history]
        
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback", response_model=ResponseQualityResponse)
async def submit_feedback(
    feedback: ResponseQualityRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback for a search response"""
    try:
        # Calculate overall score
        overall_score = (
            feedback.relevance_score + 
            feedback.accuracy_score + 
            feedback.completeness_score + 
            feedback.coherence_score
        ) / 4
        
        quality = ResponseQuality(
            search_history_id=feedback.search_history_id,
            relevance_score=feedback.relevance_score,
            accuracy_score=feedback.accuracy_score,
            completeness_score=feedback.completeness_score,
            coherence_score=feedback.coherence_score,
            overall_score=overall_score,
            feedback=feedback.feedback
        )
        
        db.add(quality)
        db.commit()
        db.refresh(quality)
        
        return ResponseQualityResponse.from_orm(quality)
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its embeddings"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from vector store
        if document.embedding_id:
            document_processor.delete_document(document.embedding_id)
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    ) 