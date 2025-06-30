# instance/config.py

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get values from .env
#SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/resume.db")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'resume.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
OPTIMIZED_FOLDER = os.getenv("OPTIMIZED_FOLDER", "optimized")

import os

# Get absolute path to the instance folder

