"""
Test configuration and fixtures for the Sentiment Analyzer test suite.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application components
from app.app import app
from config import TestingConfig


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config.from_object(TestingConfig())
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_model():
    """Mock the sentiment analysis model for testing."""
    mock = MagicMock()
    mock.predict.return_value = ("Positive", 0.95)
    return mock


@pytest.fixture
def sample_texts():
    """Sample texts for testing different scenarios."""
    return {
        'positive': [
            "This restaurant is amazing!",
            "I love this product so much!",
            "Excellent service and great quality!",
            "Best purchase I've ever made!"
        ],
        'negative': [
            "This is terrible service.",
            "Worst experience ever.",
            "I hate this product.",
            "Complete waste of money."
        ],
        'neutral': [
            "The weather is okay today.",
            "This is a standard product.",
            "It works as expected.",
            "Average quality for the price."
        ],
        'edge_cases': [
            "",  # Empty string
            "   ",  # Whitespace only
            "a",  # Single character
            "Hi",  # Very short
            "This is a test. " * 100,  # Very long (1600+ chars)
            "🚀 Emoji test! 😊 👍",  # With emojis
            "Special chars: @#$%^&*()",  # Special characters
        ]
    }


@pytest.fixture
def api_headers():
    """Standard headers for API requests."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


class TestConfig:
    """Test configuration constants."""
    MAX_TEXT_LENGTH = 1000
    API_TIMEOUT = 5.0
    EXPECTED_RESPONSE_TIME = 1.0  # seconds
