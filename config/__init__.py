"""
Configuration module for Flask application.
Manages database, secret keys, and environment settings.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class following SOLID principles."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///fashion_brand.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Pagination
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in development


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # SESSION_COOKIE_SECURE already set to True in base Config
    
    # Custom domain configuration - Support both root and www
    # Don't set SERVER_NAME to allow both rootsfashion.in and www.rootsfashion.in
    PREFERRED_URL_SCHEME = 'https'
    
    # Security headers for production
    # Use wildcard subdomain to support both root and www
    SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', '.rootsfashion.in')
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Force HTTPS
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
