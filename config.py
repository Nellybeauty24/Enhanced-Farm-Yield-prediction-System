import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-now')
    CORS_HEADERS = 'Content-Type'
    
    # Database Configuration
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(PROJECT_ROOT, 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
