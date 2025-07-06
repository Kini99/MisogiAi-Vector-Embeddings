#!/usr/bin/env python3
"""
Setup script for the Intelligent Customer Support System
Automates installation and initialization
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Print a step with description"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print_step(2, "Installing Dependencies")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables"""
    print_step(3, "Setting Up Environment")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created")
        print("⚠️  Please edit .env file and add your Google Gemini API key")
        print("   You can get an API key from: https://makersuite.google.com/app/apikey")
        return False
    else:
        print("✅ .env file already exists")
        
        # Check if API key is set
        with open(env_file, 'r') as f:
            content = f.read()
        
        if "your_google_gemini_api_key_here" in content:
            print("⚠️  Please edit .env file and add your Google Gemini API key")
            return False
        
        print("✅ API key appears to be configured")
        return True

def start_api_server():
    """Start the API server"""
    print_step(4, "Starting API Server")
    
    print("🚀 Starting API server in background...")
    try:
        # Start API server in background
        process = subprocess.Popen([sys.executable, "api.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health/", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running at http://localhost:8000")
                return process
            else:
                print("❌ API server failed to start properly")
                return None
        except requests.exceptions.RequestException:
            print("❌ API server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def initialize_sample_data():
    """Initialize the system with sample data"""
    print_step(5, "Initializing Sample Data")
    
    try:
        subprocess.check_call([sys.executable, "init_sample_data.py"])
        print("✅ Sample data initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize sample data: {e}")
        return False

def run_demo():
    """Run the demo to verify everything works"""
    print_step(6, "Running Demo")
    
    try:
        subprocess.check_call([sys.executable, "demo.py"])
        print("✅ Demo completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete!")
    
    print("🎉 Your Intelligent Customer Support System is ready!")
    print("\n📋 Next Steps:")
    print("1. Start the Streamlit frontend:")
    print("   streamlit run streamlit_app.py")
    print("\n2. Access the web interface:")
    print("   http://localhost:8501")
    print("\n3. View API documentation:")
    print("   http://localhost:8000/docs")
    print("\n4. Try the demo:")
    print("   python demo.py")
    print("\n📚 Documentation:")
    print("   README.md - Complete system documentation")
    print("\n🔧 Configuration:")
    print("   .env - Environment variables")
    print("   api.py - API server configuration")
    print("\n🎯 Features to try:")
    print("   • Submit a new ticket and see AI analysis")
    print("   • View automatic categorization and priority assignment")
    print("   • Check generated responses and confidence scores")
    print("   • Explore the analytics dashboard")
    print("   • Manage the knowledge base")

def main():
    """Main setup function"""
    print("🎫 Intelligent Customer Support System - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n⚠️  Please configure your API key and run setup again")
        print("   Edit .env file and add your Google Gemini API key")
        sys.exit(1)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        sys.exit(1)
    
    # Initialize sample data
    if not initialize_sample_data():
        print("⚠️  Sample data initialization failed, but system should still work")
    
    # Run demo
    if not run_demo():
        print("⚠️  Demo failed, but system should still work")
    
    # Clean up API process
    try:
        api_process.terminate()
        api_process.wait(timeout=5)
    except:
        api_process.kill()
    
    print_next_steps()

if __name__ == "__main__":
    main() 