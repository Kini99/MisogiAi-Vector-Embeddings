#!/usr/bin/env python3
"""
Setup script for Research Assistant
Automates installation and configuration
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Setup environment file"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ env.example not found")

def install_dependencies():
    """Install Python dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return False
    return True

def initialize_database():
    """Initialize the database"""
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    from config import config
    
    missing_keys = []
    
    if not config.GOOGLE_API_KEY:
        missing_keys.append("GOOGLE_API_KEY")
    
    if not config.SERPER_API_KEY and not config.BING_API_KEY:
        missing_keys.append("SERPER_API_KEY or BING_API_KEY (optional)")
    
    if missing_keys:
        print("⚠️  Missing API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("Please add them to your .env file")
        return False
    
    print("✅ API keys configured")
    return True

def download_models():
    """Download required models"""
    try:
        print("🔄 Downloading models (this may take a while)...")
        
        # Import and initialize models to trigger download
        from sentence_transformers import SentenceTransformer
        from sentence_transformers import CrossEncoder
        
        # Download embedding model
        print("📥 Downloading embedding model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Download cross-encoder model
        print("📥 Downloading cross-encoder model...")
        cross_encoder = CrossEncoder("ms-marco-MiniLM-L-12-v2")
        
        print("✅ Models downloaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download models: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print("🧪 Running basic tests...")
    
    # Test imports
    try:
        from config import config
        from database import get_db
        from models import User, Document
        from document_processor import DocumentProcessor
        from web_search import WebSearchEngine
        from hybrid_search import HybridSearchEngine
        from rag_engine import RAGEngine
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Research Assistant Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        sys.exit(1)
    
    # Download models
    if not download_models():
        print("❌ Setup failed at model download")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Setup failed at testing")
        sys.exit(1)
    
    # Check API keys
    check_api_keys()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Start the backend: uvicorn main:app --reload")
    print("3. Start the frontend: streamlit run streamlit_app.py")
    print("4. Visit http://localhost:8000/docs for API documentation")
    print("5. Visit http://localhost:8501 for the web interface")

if __name__ == "__main__":
    main() 