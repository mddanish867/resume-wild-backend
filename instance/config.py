import os
from datetime import timedelta
from pathlib import Path

# Get absolute path to the instance folder (where this config file is located)
BASE_DIR = Path(__file__).parent.parent.absolute()  # Go up one level from instance/
INSTANCE_DIR = Path(__file__).parent.absolute()     # instance/ directory

# Ensure required directories exist
(BASE_DIR / 'uploads').mkdir(exist_ok=True)
(BASE_DIR / 'optimized').mkdir(exist_ok=True)
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# Database configuration - Use absolute path
DB_PATH = INSTANCE_DIR / 'paper-brain-resume.db'
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change-in-production')
WTF_CSRF_ENABLED = False  # Disable CSRF for API endpoints

# File upload configuration
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
UPLOAD_FOLDER = str(BASE_DIR / 'uploads')
OPTIMIZED_FOLDER = str(BASE_DIR / 'optimized')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'docx'}

# Session configuration
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# API Configuration
API_TITLE = "Resume Optimizer API"
API_VERSION = "v1.0"

# Resume optimization settings
OPTIMIZATION_SETTINGS = {
    'max_keywords_per_section': {
        'skills': 8,
        'experience': 5,
        'projects': 4,
        'summary': 3,
        'other': 2
    },
    'global_keyword_limit': 15,
    'keyword_density_limit': 0.03,  # 3% max density
    'min_job_description_length': 50,
    'max_job_description_length': 5000,
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'app.log'),
            'level': 'INFO',
            'formatter': 'detailed',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'logs' / 'errors.log'),
            'level': 'ERROR',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Environment-specific settings
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
TESTING = os.getenv('FLASK_TESTING', 'False').lower() == 'true'

# CORS settings
CORS_SETTINGS = {
    'origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization'],
    'supports_credentials': True
}

# Performance settings
PERFORMANCE_SETTINGS = {
    'pdf_conversion_timeout': 30,  # seconds
    'optimization_timeout': 60,  # seconds
    'max_concurrent_optimizations': 5,
}

# Feature flags
FEATURE_FLAGS = {
    'enable_pdf_conversion': True,
    'enable_backup_creation': True,
    'enable_document_comparison': True,
    'enable_keyword_analytics': True,
    'enable_file_cleanup': True,
}

# Email settings (if needed for notifications)
MAIL_SETTINGS = {
    'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME', ''),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD', ''),
}

# Cache settings (for future use)
CACHE_SETTINGS = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,
}

# Rate limiting (for future implementation)
RATE_LIMITING = {
    'uploads_per_hour': 10,
    'optimizations_per_hour': 5,
    'downloads_per_hour': 20,
}

# Debug info
print(f"Config loaded:")
print(f"  DEBUG={DEBUG}")
print(f"  DATABASE={SQLALCHEMY_DATABASE_URI}")
print(f"  BASE_DIR={BASE_DIR}")
print(f"  DB_PATH={DB_PATH}")
print(f"  UPLOAD_FOLDER={UPLOAD_FOLDER}")
print(f"  OPTIMIZED_FOLDER={OPTIMIZED_FOLDER}")