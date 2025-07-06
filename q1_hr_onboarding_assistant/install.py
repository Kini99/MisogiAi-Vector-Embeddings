#!/usr/bin/env python3
"""
Installation script for HR Onboarding Knowledge Assistant
Handles dependency conflicts and provides multiple installation options
"""

import subprocess
import sys
import os
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
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3:
        print("❌ Python 3 is required")
        return False
    
    if version.minor < 8:
        print("❌ Python 3.8 or higher is required")
        return False
    
    if version.minor > 11:
        print("⚠️  Python 3.12+ may have compatibility issues with some packages")
        print("   Consider using Python 3.8-3.11")
    
    print("✅ Python version is compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

def install_requirements():
    """Install requirements"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing requirements"
    )

def install_manual_dependencies():
    """Install dependencies manually to avoid conflicts"""
    dependencies = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0", 
        "python-multipart>=0.0.6",
        "chromadb>=0.4.0",
        "openai>=1.3.0",
        "pypdf2>=3.0.0",
        "python-docx>=1.1.0",
        "sentence-transformers>=2.2.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.28.0",
        "pandas>=2.1.0",
        "numpy>=1.25.0",
        "tiktoken>=0.5.0",
        "jinja2>=3.1.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install {dep}", f"Installing {dep}"):
            return False
    return True

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        "fastapi", "uvicorn", "chromadb", "openai", 
        "PyPDF2", "docx", "sentence_transformers", 
        "streamlit", "pandas", "numpy", "pydantic", 
        "dotenv", "tiktoken", "jinja2"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists("env_example.txt"):
            print("📝 Creating .env file from template...")
            with open("env_example.txt", "r") as f:
                content = f.read()
            
            with open(".env", "w") as f:
                f.write(content)
            
            print("✅ Created .env file")
            print("⚠️  Please edit .env file and add your OpenAI API key")
            return True
        else:
            print("❌ env_example.txt not found")
            return False
    else:
        print("✅ .env file already exists")
        return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ["uploads", "chroma_db", "sample_documents"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created {directory}/")
        else:
            print(f"✅ {directory}/ already exists")

def main():
    """Main installation function"""
    print("🏢 HR Onboarding Knowledge Assistant - Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    upgrade_pip()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    
    if install_requirements():
        print("✅ Requirements installed successfully")
    else:
        print("❌ Requirements installation failed, trying manual installation...")
        
        # Fallback: Manual installation
        if install_manual_dependencies():
            print("✅ Manual installation completed")
        else:
            print("❌ Installation failed")
            print("Please see INSTALLATION_GUIDE.md for troubleshooting")
            return False
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed")
        return False
    
    # Create environment file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed successfully!")
    print("=" * 60)
    
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python setup_and_demo.py")
    print("3. Or start manually:")
    print("   - API: python run_api.py")
    print("   - Web: python run_streamlit.py")
    
    print("\n📚 For more help, see:")
    print("- README.md - Complete documentation")
    print("- INSTALLATION_GUIDE.md - Troubleshooting guide")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 