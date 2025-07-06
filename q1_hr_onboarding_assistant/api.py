from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import time
from typing import List, Optional

from config import Config
from document_processor import DocumentProcessor
from vector_store_simple import SimpleVectorStore
from rag_engine import RAGEngine
from models import (
    QueryRequest, QueryResponse, DocumentUploadResponse, DocumentStats,
    SuggestedQuestionsResponse, ErrorResponse, HealthCheckResponse,
    QueryCategory
)

# Initialize FastAPI app
app = FastAPI(
    title="HR Onboarding Knowledge Assistant",
    description="AI-powered HR assistant for new employee onboarding",
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
config = Config()
document_processor = DocumentProcessor(config)
vector_store = SimpleVectorStore(config)
rag_engine = RAGEngine(config, vector_store)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HR Onboarding Knowledge Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #0066cc; }
            .url { font-family: monospace; background: #e0e0e0; padding: 2px 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>HR Onboarding Knowledge Assistant</h1>
            <p>Welcome to the AI-powered HR assistant for new employee onboarding.</p>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/health</div>
                <p>Health check endpoint</p>
            </div>
            
            <div class="endpoint">
                <div class="method">POST</div>
                <div class="url">/query</div>
                <p>Ask HR-related questions</p>
            </div>
            
            <div class="endpoint">
                <div class="method">POST</div>
                <div class="url">/upload</div>
                <p>Upload HR documents (PDF, DOCX, TXT)</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/documents</div>
                <p>Get document statistics</p>
            </div>
            
            <div class="endpoint">
                <div class="method">GET</div>
                <div class="url">/suggestions</div>
                <p>Get suggested questions by category</p>
            </div>
            
            <div class="endpoint">
                <div class="method">DELETE</div>
                <div class="url">/documents/{document_hash}</div>
                <p>Delete a specific document</p>
            </div>
            
            <h2>Interactive API Documentation:</h2>
            <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
        </div>
    </body>
    </html>
    """

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "vector_store": "healthy" if vector_store else "unhealthy",
        "rag_engine": "healthy" if rag_engine else "unhealthy",
        "document_processor": "healthy" if document_processor else "unhealthy"
    }
    
    return HealthCheckResponse(
        status="healthy",
        services=services
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process HR-related queries"""
    try:
        # Process the query through RAG pipeline
        response = rag_engine.process_query(request.query)
        
        # Convert to Pydantic model
        return QueryResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process HR documents"""
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {config.ALLOWED_EXTENSIONS}"
            )
        
        # Save uploaded file
        file_path = os.path.join(config.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        start_time = time.time()
        chunks = document_processor.process_document(file_path, file.filename)
        
        # Add to vector store
        success = vector_store.add_documents(chunks)
        
        processing_time = time.time() - start_time
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add documents to vector store")
        
        # Get document hash from first chunk
        document_hash = chunks[0]["metadata"]["document_hash"] if chunks else "unknown"
        
        return DocumentUploadResponse(
            filename=file.filename,
            status="success",
            chunks_processed=len(chunks),
            document_hash=document_hash,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents", response_model=DocumentStats)
async def get_document_stats():
    """Get statistics about uploaded documents"""
    try:
        stats = vector_store.get_document_stats()
        return DocumentStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document stats: {str(e)}")

@app.get("/suggestions", response_model=SuggestedQuestionsResponse)
async def get_suggested_questions(category: Optional[QueryCategory] = None):
    """Get suggested questions by category"""
    try:
        questions = rag_engine.get_suggested_questions(category.value if category else None)
        return SuggestedQuestionsResponse(
            category=category,
            questions=questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")

@app.delete("/documents/{document_hash}")
async def delete_document(document_hash: str):
    """Delete a specific document by its hash"""
    try:
        success = vector_store.delete_document(document_hash)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.get("/categories", response_model=List[str])
async def get_categories():
    """Get available query categories"""
    return list(QueryCategory.__members__.keys())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT) 