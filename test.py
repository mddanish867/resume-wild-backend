# import sqlite3

# conn = sqlite3.connect("instance/resume.db")
# cursor = conn.cursor()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# print("Tables in the database:", tables)

# conn.close()

#!/usr/bin/env python3
"""
Flask app diagnostic script to identify configuration issues
"""
import os
import sys
from pathlib import Path

def test_config_loading():
    """Test if config loads properly"""
    print("1. Testing config loading...")
    try:
        sys.path.insert(0, ".")
        from instance.config import SQLALCHEMY_DATABASE_URI, BASE_DIR
        print(f"   ✓ Config loaded successfully")
        print(f"   DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
        print(f"   BASE_DIR: {BASE_DIR}")
        return True
    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_import():
    """Test Flask app import"""
    print("2. Testing Flask app import...")
    try:
        sys.path.insert(0, ".")
        from app import create_app
        print("   ✓ Flask app import successful")
        return True
    except Exception as e:
        print(f"   ❌ Flask app import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """Test Flask app creation without database"""
    print("3. Testing Flask app creation...")
    try:
        sys.path.insert(0, ".")
        from app import create_app
        
        # Create app but don't initialize database
        app = create_app()
        print(f"   ✓ Flask app created successfully")
        print(f"   App config DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
        return app
    except Exception as e:
        print(f"   ❌ Flask app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_database_initialization(app):
    """Test database initialization separately"""
    print("4. Testing database initialization...")
    try:
        sys.path.insert(0, ".")
        from app import db
        
        with app.app_context():
            # Check if we can connect
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   Using URI: {db_uri}")
            
            # Try to create tables
            db.create_all()
            print("   ✓ Database tables created successfully")
            
            # Test a simple query
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"   ✓ Tables created: {tables}")
            
            return True
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test environment variables"""
    print("5. Testing environment variables...")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"   ✓ .env file exists: {env_file.absolute()}")
        content = env_file.read_text()
        print("   .env content:")
        for line in content.split('\n'):
            if line.strip() and not line.startswith('#'):
                print(f"     {line}")
    else:
        print("   ⚠️  No .env file found")
    
    # Check relevant environment variables
    print("   Environment variables:")
    env_vars = ['DATABASE_URL', 'FLASK_DEBUG', 'SECRET_KEY']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive info
            display_value = value if var != 'SECRET_KEY' else '***HIDDEN***'
            print(f"     {var}={display_value}")
        else:
            print(f"     {var}=NOT SET")

def check_file_structure():
    """Check project file structure"""
    print("6. Checking project structure...")
    
    required_files = [
        'app/__init__.py',
        'app/models.py',
        'instance/config.py',
        'run.py',
        'requirements.txt'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    # Check directories
    required_dirs = ['uploads', 'optimized', 'logs', 'instance']
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✓ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ - MISSING")

def main():
    print("Flask App Diagnostic Script")
    print("=" * 50)
    
    check_file_structure()
    print()
    
    test_environment_variables()
    print()
    
    if not test_config_loading():
        print("❌ Cannot proceed - config loading failed")
        return
    
    print()
    
    if not test_flask_import():
        print("❌ Cannot proceed - Flask app import failed")
        return
    
    print()
    
    app = test_app_creation()
    if not app:
        print("❌ Cannot proceed - Flask app creation failed")
        return
    
    print()
    
    test_database_initialization(app)
    
    print("\n" + "=" * 50)
    print("Diagnostic complete!")

if __name__ == "__main__":
    main()