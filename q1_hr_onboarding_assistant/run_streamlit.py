#!/usr/bin/env python3
"""
HR Onboarding Knowledge Assistant - Streamlit Interface
Run this script to start the Streamlit web interface
"""

import subprocess
import sys
import os

def main():
    """Start the Streamlit web interface"""
    print("🏢 Starting HR Onboarding Knowledge Assistant - Web Interface...")
    print("🌐 Streamlit will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    main() 