from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Initialize database
db = SQLAlchemy()

def create_app():
    # Create Flask app with instance-relative config
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    # Ensure required folders exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("optimized", exist_ok=True)

    # Load configuration from instance/config.py
    app.config.from_pyfile("config.py")

    # Show DB path for debugging (optional but helpful)
    print(f"Using DB path: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize the SQLAlchemy app
    db.init_app(app)

    # Register blueprint
    from .routes import resume_bp
    app.register_blueprint(resume_bp)
    # app.register_blueprint(resume_bp, url_prefix="/api")

    # Create tables within app context
    with app.app_context():
        db.create_all()

    return app
