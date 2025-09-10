#!/usr/bin/env python3
"""
Setup script for Resume Optimizer
This script helps set up the application with all required dependencies and configurations.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description=""):
    """Run a system command and handle errors"""
    try:
        logger.info(f"Running: {description or command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 8):
        logger.error(f"Python 3.8+ required, but you have {version.major}.{version.minor}")
        return False
    logger.info(f"Python version {version.major}.{version.minor}.{version.micro} ✓")
    return True

def create_directories():
    """Create required directories"""
    directories = [
        "uploads",
        "optimized", 
        "logs",
        "instance",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory} ✓")

def install_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install main requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def setup_nltk():
    """Download required NLTK data"""
    logger.info("Setting up NLTK data...")
    
    nltk_setup_code = '''
import ssl
import nltk

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.download('punkt', quiet=True)
    print("NLTK punkt tokenizer downloaded successfully")
except Exception as e:
    print(f"NLTK download failed: {e}")
'''
    
    return run_command(f'{sys.executable} -c "{nltk_setup_code}"', "Downloading NLTK data")

def setup_spacy_optional():
    """Optionally install SpaCy model"""
    logger.info("SpaCy model installation (optional)...")
    
    try:
        logger.info("SpaCy is installed")
        
        # Try to download English model
        if run_command(f"{sys.executable} -m spacy download en_core_web_sm", "Downloading SpaCy English model"):
            logger.info("SpaCy English model installed ✓")
        else:
            logger.warning("SpaCy model download failed (optional feature)")
            
    except ImportError:
        logger.info("SpaCy not installed, skipping model download")

def create_config_files():
    """Create configuration files if they don't exist"""
    
    # Create .env file
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Flask settings
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Database
DATABASE_URL=sqlite:///resume_optimizer.db

# Security (Change this in production!)
SECRET_KEY=dev-secret-key-change-in-production

# File settings
UPLOAD_FOLDER=uploads
OPTIMIZED_FOLDER=optimized
"""
        env_file.write_text(env_content)
        logger.info("Created .env file ✓")
    
    # Create instance/config.py if it doesn't exist
    config_file = Path("instance/config.py")
    if not config_file.exists():
        logger.info("instance/config.py already provided ✓")

def test_installation():
    """Test if the installation works"""
    logger.info("Testing installation...")
    
    test_code = '''
try:
    # Test imports
    from flask import Flask
    from transformers import pipeline
    import nltk
    from docx import Document
    import sklearn
    
    print("✓ All core dependencies imported successfully")
    
    # Test NLTK
    from nltk.tokenize import sent_tokenize
    sent_tokenize("This is a test sentence. This is another one.")
    print("✓ NLTK working")
    
    # Test document creation
    from docx import Document
    doc = Document()
    doc.add_paragraph("Test")
    print("✓ python-docx working")
    
    print("🎉 Installation test successful!")
    
except Exception as e:
    print(f"❌ Installation test failed: {e}")
    exit(1)
'''
    
    return run_command(f'{sys.executable} -c "{test_code}"', "Testing installation")

def setup_database():
    """Initialize the database"""
    logger.info("Setting up database...")
    
    db_setup_code = '''
import os
import sys
sys.path.append(".")

try:
    from app import create_app, db
    
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully")
except Exception as e:
    print(f"❌ Database setup failed: {e}")
    sys.exit(1)
'''
    
    return run_command(f'{sys.executable} -c "{db_setup_code}"', "Initializing database")

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start the application:")
    print("   python run.py")
    print("\n2. Test the API:")
    print("   curl http://127.0.0.1:5000/health")
    print("\n3. Upload a resume:")
    print("   Use POST /upload/ with a DOCX file")
    print("\n4. Optimize resume:")
    print("   Use POST /optimize-resume/{resume_id}")
    print("\n5. Download result:")
    print("   Use GET /download-resume/{resume_id}")
    
    print("\n📁 Important directories:")
    print("   - uploads/    : Original resumes")
    print("   - optimized/  : Processed resumes")
    print("   - logs/       : Application logs")
    
    print("\n🔧 Configuration:")
    print("   - Edit instance/config.py for advanced settings")
    print("   - Edit .env for environment variables")
    
    print("\n📖 Documentation:")
    print("   - See README.md for detailed API documentation")
    print("   - Check logs/ for debugging information")
    print("\n" + "="*60)

def main():
    """Main setup function"""
    print("Resume Optimizer Setup Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    logger.info("Creating required directories...")
    create_directories()
    
    # Install dependencies
    logger.info("Installing dependencies...")
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Setup NLTK
    if not setup_nltk():
        logger.warning("NLTK setup failed, but continuing...")
    
    # Setup SpaCy (optional)
    setup_spacy_optional()
    
    # Create config files
    logger.info("Creating configuration files...")
    create_config_files()
    
    # Setup database
    if not setup_database():
        logger.error("Database setup failed")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        logger.error("Installation test failed")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        sys.exit(1)