# Lecture Intelligence - RAG-Powered Learning Assistant

A comprehensive application that processes lecture videos, generates transcripts, and enables natural language conversations with lecture content using RAG (Retrieval-Augmented Generation) architecture.

## Features

- **Video Upload**: Support for 2-3 hour lecture videos
- **Automated Transcription**: Speech-to-text using OpenAI Whisper
- **RAG Pipeline**: Advanced retrieval with timestamp preservation
- **Interactive Chat**: Natural language Q&A with lecture content
- **Timestamp References**: Direct links to video moments
- **Context-Aware Responses**: Intelligent retrieval of relevant segments

## Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ RAG Pipeline
                                    ↓
                              Vector Database (ChromaDB)
                                    ↓
                              Video Processing & Transcription
```

## Tech Stack

- **Backend**: FastAPI, LangChain, OpenAI
- **Frontend**: React, TypeScript, Tailwind CSS
- **Database**: ChromaDB (Vector), PostgreSQL (Metadata)
- **Video Processing**: MoviePy, Whisper
- **Task Queue**: Celery, Redis

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- FFmpeg (for video processing)
- OpenAI API Key

### Installation

1. **Clone and setup backend:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other settings
```

2. **Setup frontend:**
```bash
cd frontend
npm install
```

3. **Run the application:**
```bash
# Backend
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm start
```

## Usage

1. **Upload Lecture Video**: Drag and drop or select a video file
2. **Wait for Processing**: Video is transcribed and chunked automatically
3. **Start Chatting**: Ask questions about the lecture content
4. **Get Timestamped Answers**: Click timestamps to jump to video moments

## Sample Queries

- "What did the professor say about machine learning algorithms?"
- "Explain the concept discussed around minute 45"
- "Summarize the key points from the first hour"
- "What examples were given for neural networks?"

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## License

MIT License 