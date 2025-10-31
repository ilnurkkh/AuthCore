import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Set Flask configuration variables from .env file."""

    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_default_fallback_secret_key')

    # Database
    # Provide a simple default. This will be OVERRIDDEN in app.py.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Enhancements (Level 2)
    LOCKOUT_ATTEMPTS = 3
    LOCKOUT_DURATION_MINUTES = 2
