# Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- FFmpeg (for video processing)
- OpenAI API Key

## Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp backend.env.example .env
   # Edit .env with your OpenAI API key and other settings
   ```

3. **Install FFmpeg:**
   - **macOS:** `brew install ffmpeg`
   - **Ubuntu/Debian:** `sudo apt install ffmpeg`
   - **Windows:** Download from https://ffmpeg.org/download.html

4. **Run the backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp frontend.env.example .env
   # Edit .env if you need to change the API URL
   ```

4. **Run the frontend:**
   ```bash
   npm start
   ```

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `CHROMA_PERSIST_DIRECTORY`: Vector database storage location
- `UPLOAD_DIR`: Video file storage location
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 500MB)

### Frontend (.env)
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000/api/v1)

## Usage

1. Open http://localhost:3000 in your browser
2. Upload a lecture video (MP4, AVI, MOV, MKV, WebM)
3. Wait for processing to complete
4. Navigate to the Chat page
5. Select your lecture and start asking questions

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Troubleshooting

- **Video processing fails:** Ensure FFmpeg is installed and in your PATH
- **OpenAI errors:** Check your API key and billing status
- **CORS errors:** Verify the frontend URL is in BACKEND_CORS_ORIGINS
- **Database errors:** Check DATABASE_URL and ensure write permissions 