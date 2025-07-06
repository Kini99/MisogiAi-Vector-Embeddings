import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Lecture Intelligence"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./lecture_intelligence.db")
    
    # Vector Database Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # Video Processing
    SUPPORTED_VIDEO_FORMATS: list = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    SUPPORTED_AUDIO_FORMATS: list = [".mp3", ".wav", ".m4a", ".flac"]
    
    # RAG Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Redis Configuration (for Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    class Config:
        case_sensitive = True

settings = Settings() 