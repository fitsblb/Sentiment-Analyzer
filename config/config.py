"""
Configuration management for the Sentiment Analyzer application.
Handles environment variables, settings, and application configuration.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST: str = os.getenv('HOST', '127.0.0.1')
    PORT: int = int(os.getenv('PORT', 5000))
    
    # Model settings
    MODEL_NAME: str = os.getenv('MODEL_NAME', 'fitsblb/YelpReviewsAnalyzer')
    MODEL_CACHE_DIR: Optional[str] = os.getenv('MODEL_CACHE_DIR', None)
    MAX_TEXT_LENGTH: int = int(os.getenv('MAX_TEXT_LENGTH', 1000))
    
    # API settings
    API_RATE_LIMIT: str = os.getenv('API_RATE_LIMIT', '100 per hour')
    API_PREFIX: str = os.getenv('API_PREFIX', '/api')
    
    # Logging settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 
                                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE: Optional[str] = os.getenv('LOG_FILE', None)
    
    # Performance settings
    MODEL_BATCH_SIZE: int = int(os.getenv('MODEL_BATCH_SIZE', 1))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # Security settings
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    MAX_CONTENT_LENGTH: int = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024))  # 16KB


@dataclass
class DevelopmentConfig(Config):
    """Development configuration with debug settings."""
    DEBUG: bool = True
    LOG_LEVEL: str = 'DEBUG'


@dataclass  
class ProductionConfig(Config):
    """Production configuration with security and performance optimizations."""
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv('SECRET_KEY', None)
    LOG_LEVEL: str = 'WARNING'
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', 'https://yourdomain.com')
    
    def __post_init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production!")


@dataclass
class TestingConfig(Config):
    """Testing configuration for unit tests."""
    DEBUG: bool = True
    TESTING: bool = True
    MODEL_NAME: str = 'distilbert-base-uncased-finetuned-sst-2-english'  # Smaller model for testing
    LOG_LEVEL: str = 'ERROR'


def get_config() -> Config:
    """
    Get the appropriate configuration based on the environment.
    
    Returns:
        Config: Configuration object based on FLASK_ENV environment variable
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Global config instance
config = get_config()
