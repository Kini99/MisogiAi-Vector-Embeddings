#!/usr/bin/env python3
"""
Setup and Demo Script for HR Onboarding Knowledge Assistant
This script handles initial setup and demonstrates the system capabilities
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔧 Checking dependencies...")
    
    required_packages = [
        "fastapi", "uvicorn", "chromadb", "openai",
        "PyPDF2", "docx", "sentence_transformers", "streamlit"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found")
        print("Creating .env file from template...")
        
        if os.path.exists("env_example.txt"):
            with open("env_example.txt", "r") as f:
                env_content = f.read()
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            print("✅ Created .env file")
            print("⚠️  Please edit .env file and add your OpenAI API key")
            return False
        else:
            print("❌ env_example.txt not found")
            return False
    
    # Check OpenAI API key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            print("⚠️  OpenAI API key not configured in .env file")
            print("Please add your OpenAI API key to the .env file")
            return False
        
        print("✅ OpenAI API key configured")
        return True
        
    except Exception as e:
        print(f"❌ Error checking environment: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = ["uploads", "chroma_db", "sample_documents"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/")
        else:
            print(f"✅ {directory}/ already exists")

def upload_sample_document():
    """Upload the sample employee handbook"""
    print("\n📄 Uploading sample document...")
    
    sample_doc_path = "sample_documents/employee_handbook.txt"
    
    if not os.path.exists(sample_doc_path):
        print("❌ Sample document not found")
        return False
    
    try:
        with open(sample_doc_path, "rb") as f:
            files = {"file": ("employee_handbook.txt", f, "text/plain")}
            response = requests.post("http://localhost:8000/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sample document uploaded successfully!")
            print(f"   - Chunks processed: {result['chunks_processed']}")
            print(f"   - Processing time: {result['processing_time']:.2f}s")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        return False
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return False

def test_basic_functionality():
    """Test basic system functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test a simple query
        test_query = {
            "query": "How many vacation days do I get as a new employee?"
        }
        
        response = requests.post("http://localhost:8000/query", json=test_query)
        if response.status_code == 200:
            result = response.json()
            print("✅ Query endpoint working")
            print(f"   - Category: {result['query_category']}")
            print(f"   - Confidence: {result['confidence']}")
            print(f"   - Sources: {len(result['sources'])}")
            return True
        else:
            print(f"❌ Query endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API server not running")
        return False
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        return False

def start_api_server():
    """Start the API server in the background"""
    print("\n🚀 Starting API server...")
    
    try:
        # Start the server in a subprocess
        process = subprocess.Popen([
            sys.executable, "run_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for the server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server started successfully")
                return process
            else:
                print("❌ API server failed to start properly")
                return None
        except:
            print("❌ API server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def main():
    """Main setup and demo function"""
    print("🏢 HR Onboarding Knowledge Assistant - Setup & Demo")
    print("=" * 60)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Step 2: Check environment
    if not check_environment():
        print("\n❌ Please configure your environment first")
        return
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Start API server
    server_process = start_api_server()
    if not server_process:
        print("\n❌ Failed to start API server")
        return
    
    try:
        # Step 5: Upload sample document
        if not upload_sample_document():
            print("\n⚠️  Failed to upload sample document")
            print("You can upload documents manually through the web interface")
        
        # Step 6: Test functionality
        if not test_basic_functionality():
            print("\n❌ Basic functionality test failed")
            return
        
        # Step 7: Provide next steps
        print("\n" + "=" * 60)
        print("🎉 Setup completed successfully!")
        print("=" * 60)
        
        print("\n📋 Next steps:")
        print("1. 🌐 Web Interface: http://localhost:8501")
        print("   Run: python run_streamlit.py")
        
        print("2. 📚 API Documentation: http://localhost:8000/docs")
        print("   Run: python run_api.py")
        
        print("3. 🧪 Run tests: python test_system.py")
        
        print("4. 🎬 Run demo: python demo_queries.py")
        
        print("\n💡 Tips:")
        print("- Upload your own HR documents through the web interface")
        print("- Try different types of questions about policies and benefits")
        print("- Check the API documentation for advanced usage")
        
        print("\n🔄 The API server is running in the background")
        print("Press Ctrl+C to stop this script (server will continue running)")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Setup script stopped. API server may still be running.")
            
    finally:
        # Clean up
        if server_process:
            print("🛑 Stopping API server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main() 