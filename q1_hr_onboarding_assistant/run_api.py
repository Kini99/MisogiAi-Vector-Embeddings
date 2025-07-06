#!/usr/bin/env python3
"""
HR Onboarding Knowledge Assistant - API Server
Run this script to start the FastAPI server
"""

import uvicorn
from config import Config

def main():
    """Start the FastAPI server"""
    config = Config()
    
    print("🏢 Starting HR Onboarding Knowledge Assistant...")
    print(f"📡 Server will be available at: http://{config.HOST}:{config.PORT}")
    print(f"📚 API Documentation: http://{config.HOST}:{config.PORT}/docs")
    print(f"📖 ReDoc Documentation: http://{config.HOST}:{config.PORT}/redoc")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "api:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 