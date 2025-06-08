#!/usr/bin/env python3
"""
Startup script for PlantCare AI application.
Checks dependencies and starts the application.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary',
        'python-jose', 'passlib', 'torch', 'ultralytics',
        'transformers', 'opencv-python', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_models():
    """Check if AI models are available"""
    model_paths = [
        Path("Chatbot/modelv4"),
        Path("runs/medium_model/train/medium_plant_disease_exp2/weights/best.pt")
    ]
    
    missing_models = []
    
    for model_path in model_paths:
        if not model_path.exists():
            missing_models.append(str(model_path))
    
    if missing_models:
        print("⚠️  Some AI models are missing:")
        for model in missing_models:
            print(f"   - {model}")
        print("\nThe application will start but some features may not work.")
        print("Please ensure your trained models are in the correct locations.")
        return False
    
    print("✅ AI models found")
    return True

def check_database():
    """Check database connection"""
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. Database credentials are correct in config.py")
        print("3. Database has been initialized with: python setup_database.py")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'outputs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Required directories created")

def start_application():
    """Start the FastAPI application"""
    print("\n🚀 Starting PlantCare AI application...")
    print("=" * 50)
    
    try:
        import uvicorn
        from main import app
        
        print("🌿 PlantCare AI is starting...")
        print("📱 Open your browser to: http://localhost:8000")
        print("🛑 Press Ctrl+C to stop the application")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 PlantCare AI stopped gracefully")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🌿 PlantCare AI - Startup Check")
    print("=" * 40)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("AI Models", check_models),
        ("Database", check_database),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            failed_checks.append(check_name)
    
    # Create directories
    print(f"\n📁 Creating directories...")
    create_directories()
    
    # Summary
    print(f"\n📋 Startup Check Summary")
    print("=" * 30)
    
    if failed_checks:
        print("❌ Some checks failed:")
        for check in failed_checks:
            print(f"   - {check}")
        
        # Ask if user wants to continue anyway
        if "Database" in failed_checks:
            print("\n⚠️  Database check failed. Cannot start without database.")
            sys.exit(1)
        
        continue_anyway = input("\nContinue anyway? (y/N): ").lower().strip()
        if continue_anyway not in ['y', 'yes']:
            print("Startup cancelled.")
            sys.exit(1)
    else:
        print("✅ All checks passed!")
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main() 