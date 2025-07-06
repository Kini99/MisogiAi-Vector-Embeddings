# HR Onboarding Knowledge Assistant

An AI-powered HR assistant that replaces time-consuming HR induction calls with an intelligent system that allows new employees to instantly query company policies, benefits, leave policies, and employment terms from uploaded HR documents.

## 🚀 Features

### Core Functionality
- **Multi-format Document Ingestion**: Support for PDF, DOCX, and TXT files
- **Intelligent Text Chunking**: HR-specific document processing with semantic understanding
- **Vector Embedding Storage**: ChromaDB-based vector database with metadata filtering
- **Conversational Interface**: Natural language query processing with context-aware responses
- **Policy Citations**: Automatic source references and document citations
- **Query Categorization**: Intelligent classification into HR categories (benefits, leave, conduct, etc.)

### Technical Implementation
- **RAG Pipeline**: Retrieval-Augmented Generation with OpenAI GPT-3.5-turbo
- **Vector Database**: ChromaDB with sentence-transformers embeddings
- **API Framework**: FastAPI with comprehensive REST endpoints
- **Web Interface**: Streamlit-based modern UI with chat interface
- **Document Management**: Admin dashboard for document upload and management

## 📋 Requirements

### System Requirements
- Python 3.8+
- 4GB+ RAM (for embedding model)
- OpenAI API key

### Dependencies
All dependencies are listed in `requirements.txt` with compatible versions:
- FastAPI & Uvicorn (API framework)
- ChromaDB (vector database)
- OpenAI (LLM integration)
- PyPDF2 & python-docx (document processing)
- Sentence-transformers (embeddings)
- Streamlit (web interface)
- Pydantic (data validation)
- Python-dotenv (environment management)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   cd q1_hr_onboarding_assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env with your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Create necessary directories**
   ```bash
   mkdir uploads
   mkdir chroma_db
   ```

## 🚀 Quick Start

### 1. Start the API Server
```bash
python run_api.py
```
The API will be available at `http://localhost:8000`

### 2. Start the Web Interface (Optional)
```bash
python run_streamlit.py
```
The web interface will be available at `http://localhost:8501`

### 3. Test the System
```bash
python test_system.py
```

## 📖 Usage Guide

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Upload Documents
```bash
POST /upload
# Upload PDF, DOCX, or TXT files
```

#### Query HR Policies
```bash
POST /query
{
  "query": "How many vacation days do I get as a new employee?"
}
```

#### Get Document Statistics
```bash
GET /documents
```

#### Get Suggested Questions
```bash
GET /suggestions?category=leave_policy
```

### Web Interface

1. **Chat Interface**: Natural conversation with the HR assistant
2. **Document Management**: Upload and manage HR documents
3. **Analytics**: View system statistics and usage metrics
4. **Settings**: Configure API connections and system preferences

## 📚 Sample Use Cases

The system is designed to handle common HR onboarding questions:

### Leave Policies
- "How many vacation days do I get as a new employee?"
- "What's the process for requesting parental leave?"
- "How do I request sick leave?"

### Benefits
- "How do I enroll in health insurance?"
- "What dental coverage is available?"
- "Are there vision benefits?"

### Work Arrangements
- "Can I work remotely and what are the guidelines?"
- "What's the hybrid work policy?"
- "What are the office hours?"

### General Policies
- "What's the dress code policy?"
- "How do I access the employee portal?"
- "Who should I contact for HR questions?"

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI       │    │   Vector Store  │
│   (Streamlit)   │◄──►│   (Backend)     │◄──►│   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   RAG Engine    │
                       │   (OpenAI)      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Document        │
                       │ Processor       │
                       └─────────────────┘
```

### Components

1. **Document Processor**: Handles PDF, DOCX, TXT files with HR-specific chunking
2. **Vector Store**: ChromaDB with sentence-transformers embeddings
3. **RAG Engine**: OpenAI GPT-3.5-turbo with context-aware retrieval
4. **API Layer**: FastAPI with comprehensive endpoints
5. **Web Interface**: Streamlit-based modern UI

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `CHROMA_DB_PATH`: Path to ChromaDB storage (default: `./chroma_db`)
- `SECRET_KEY`: Application secret key
- `HOST`: API server host (default: `0.0.0.0`)
- `PORT`: API server port (default: `8000`)

### Chunking Configuration
- `CHUNK_SIZE`: Maximum chunk size in characters (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_system.py
```

This will test:
- Configuration loading
- Document processing
- Vector store operations
- RAG engine functionality
- API endpoints

## 📊 Performance

### Typical Response Times
- Document upload: 2-5 seconds per document
- Query processing: 1-3 seconds
- Vector search: < 500ms

### Scalability
- Supports thousands of documents
- Concurrent user support
- Efficient vector search with metadata filtering

## 🔒 Security

- Input validation and sanitization
- File type restrictions
- API rate limiting (configurable)
- Secure document storage
- No sensitive data logging

