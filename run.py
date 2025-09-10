# from app import create_app

# app = create_app()

# if __name__ == "__main__":
#     app.run(debug=True)

    
import os
import logging
from app import create_app
from app.util import ensure_directory_structure, cleanup_old_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_application():
    """Setup application directories and cleanup old files"""
    try:
        # Ensure required directories exist
        created_dirs = ensure_directory_structure()
        if created_dirs:
            logger.info(f"Created directories: {created_dirs}")
        
        # Cleanup old files (older than 7 days)
        cleanup_old_files('uploads', max_age_days=7)
        cleanup_old_files('optimized', max_age_days=7)
        
        logger.info("Application setup completed successfully")
        
    except Exception as e:
        logger.error(f"Application setup failed: {e}")

def main():
    """Main application entry point"""
    logger.info("Starting Resume Optimizer Application")
    
    # Setup application
    setup_application()
    
    # Create Flask app
    app = create_app()
    
    # Get configuration from environment or use defaults
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Server starting on {host}:{port} (debug={debug})")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True  # Enable threading for better performance
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()