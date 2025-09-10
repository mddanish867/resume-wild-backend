from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database
db = SQLAlchemy()

def create_app():
    # Create Flask app with instance-relative config
    app = Flask(__name__, instance_relative_config=True)
    
    # Enable CORS for all routes
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])
    
    # Ensure required folders exist
    required_dirs = ["uploads", "optimized", "instance"]
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")
    
    try:
        # Load configuration from instance/config.py
        app.config.from_pyfile("config.py")
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load config file: {e}")
        # Fallback configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_optimizer.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Show DB path for debugging
    logger.info(f"Using DB path: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize the SQLAlchemy app
    db.init_app(app)
    
    # Register blueprint
    from .routes import resume_bp
    app.register_blueprint(resume_bp)
    logger.info("Blueprint registered successfully")
    
    # Create tables within app context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    return app