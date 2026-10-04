import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'foodexpress_super_secret_key_college_project_2026')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'online_food_delivery')
    
    # Check if user explicitly wants sqlite fallback for demo testing without MySQL
    USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1', 't')
    
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'food_express.db')}"
    else:
        # Standard MySQL 8 connection with PyMySQL driver
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {} if USE_SQLITE else {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Uploads & Static
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    
    # Session Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
