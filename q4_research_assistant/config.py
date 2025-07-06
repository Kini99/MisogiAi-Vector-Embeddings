import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Web Search API Configuration
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    BING_API_KEY: str = os.getenv("BING_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_assistant.db")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/research_assistant")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Vector Database Configuration
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # Search Configuration
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    HYBRID_SEARCH_WEIGHT_DENSE: float = float(os.getenv("HYBRID_SEARCH_WEIGHT_DENSE", "0.7"))
    HYBRID_SEARCH_WEIGHT_SPARSE: float = float(os.getenv("HYBRID_SEARCH_WEIGHT_SPARSE", "0.3"))
    
    # Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    RERANK_MODEL: str = os.getenv("RERANK_MODEL", "ms-marco-MiniLM-L-12-v2")
    
    # Monitoring Configuration
    ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

config = Config() 