"""
Integration tests for the Flask application.
Tests the complete application flow including routes, error handling, and responses.
"""
import pytest
import json
import time
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWebInterface:
    """Test cases for the web interface routes."""
    
    def test_home_page_get(self, client):
        """Test GET request to home page."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'AI Sentiment Analyzer' in response.data
        assert b'text_input' in response.data  # Form field present
        assert b'Analyze Sentiment' in response.data  # Submit button present
    
    @patch('app.app.predict')
    def test_home_page_post_success(self, mock_predict, client):
        """Test successful POST request to home page."""
        # Mock successful prediction
        mock_predict.return_value = ("Positive", 0.95)
        
        response = client.post('/', data={
            'text_input': 'This is a great product!'
        })
        
        assert response.status_code == 200
        assert b'Positive' in response.data
        assert b'95' in response.data  # Confidence percentage
        mock_predict.assert_called_once_with('This is a great product!')
    
    def test_home_page_post_empty_text(self, client):
        """Test POST request with empty text."""
        response = client.post('/', data={
            'text_input': ''
        })
        
        assert response.status_code == 400
        assert b'Text cannot be empty' in response.data or b'required' in response.data
    
    def test_home_page_post_long_text(self, client):
        """Test POST request with text that's too long."""
        long_text = "This is a test. " * 100  # > 1000 characters
        
        response = client.post('/', data={
            'text_input': long_text
        })
        
        assert response.status_code == 400
        assert b'under 1000 characters' in response.data or b'too long' in response.data
    
    @patch('app.app.predict')
    def test_home_page_model_error(self, mock_predict, client):
        """Test handling of model errors."""
        from app.model import ModelError
        mock_predict.side_effect = ModelError("Model failed")
        
        response = client.post('/', data={
            'text_input': 'Test text'
        })
        
        assert response.status_code == 500
        assert b'AI model is temporarily unavailable' in response.data


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'model' in data
        assert 'version' in data
        assert 'timestamp' in data
    
    def test_info_endpoint(self, client):
        """Test the API info endpoint."""
        response = client.get('/api/info')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['name'] == 'Sentiment Analyzer API'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data
        assert 'limits' in data
        assert data['limits']['max_text_length'] == 1000
    
    @patch('app.app.predict')
    def test_analyze_endpoint_success(self, mock_predict, client, api_headers):
        """Test successful sentiment analysis via API."""
        mock_predict.return_value = ("Positive", 0.95)
        
        response = client.post('/api/analyze', 
                             headers=api_headers,
                             json={'text': 'This product is amazing!'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['sentiment'] == 'Positive'
        assert data['confidence'] == 0.95
        assert 'processing_time' in data
        assert 'text_length' in data
        assert data['text_length'] == 23
    
    def test_analyze_endpoint_empty_text(self, client, api_headers):
        """Test API with empty text."""
        response = client.post('/api/analyze',
                             headers=api_headers, 
                             json={'text': ''})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Validation Error'
    
    def test_analyze_endpoint_missing_text(self, client, api_headers):
        """Test API with missing text field."""
        response = client.post('/api/analyze',
                             headers=api_headers,
                             json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Validation Error'
    
    def test_analyze_endpoint_long_text(self, client, api_headers):
        """Test API with text that's too long."""
        long_text = "This is a test. " * 100
        
        response = client.post('/api/analyze',
                             headers=api_headers,
                             json={'text': long_text})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Validation Error'
        assert 'under 1000 characters' in data['message']
    
    def test_analyze_endpoint_non_json(self, client):
        """Test API with non-JSON content."""
        response = client.post('/api/analyze',
                             headers={'Content-Type': 'text/plain'},
                             data='not json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Bad Request'
    
    @patch('app.app.predict')
    def test_analyze_endpoint_model_error(self, mock_predict, client, api_headers):
        """Test API handling of model errors."""
        from app.model import ModelError
        mock_predict.side_effect = ModelError("Model failed")
        
        response = client.post('/api/analyze',
                             headers=api_headers,
                             json={'text': 'Test text'})
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['error'] == 'Model Error'
    
    @patch('app.app.predict')
    def test_analyze_endpoint_performance(self, mock_predict, client, api_headers):
        """Test API response time performance."""
        mock_predict.return_value = ("Positive", 0.95)
        
        start_time = time.time()
        response = client.post('/api/analyze',
                             headers=api_headers,
                             json={'text': 'Performance test'})
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Response should be fast (under 1 second for mocked model)
        response_time = end_time - start_time
        assert response_time < 1.0
        
        # Check processing_time in response
        data = json.loads(response.data)
        assert 'processing_time' in data
        assert isinstance(data['processing_time'], (int, float))


class TestErrorHandling:
    """Test cases for error handling across the application."""
    
    def test_404_error(self, client):
        """Test 404 error for non-existent routes."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 error for incorrect HTTP methods."""
        response = client.put('/')  # PUT not allowed on home route
        assert response.status_code == 405
    
    def test_request_too_large(self, client):
        """Test handling of requests that are too large."""
        # This tests the MAX_CONTENT_LENGTH setting
        huge_data = 'x' * (20 * 1024)  # 20KB (larger than 16KB limit)
        
        response = client.post('/', data={'text_input': huge_data})
        # Should get 413 (Request Entity Too Large) or 400 (Bad Request)
        assert response.status_code in [400, 413]


class TestInputValidation:
    """Test cases for input validation logic."""
    
    @pytest.mark.parametrize("text,expected_valid", [
        ("Hello world", True),
        ("", False),
        ("   ", False), 
        ("a", False),  # Too short
        ("Hi", False),  # Too short
        ("This is valid text for testing.", True),
        ("x" * 1001, False),  # Too long
        ("🚀 Emoji test! 😊", True),
        ("Special chars: @#$%", True),
    ])
    def test_text_validation_cases(self, text, expected_valid, client, api_headers):
        """Test various text validation scenarios."""
        response = client.post('/api/analyze',
                             headers=api_headers,
                             json={'text': text})
        
        if expected_valid:
            # Should be 200 or 503 (if model fails), but not 400
            assert response.status_code in [200, 503]
        else:
            # Should be 400 (validation error)
            assert response.status_code == 400


class TestApplicationConfiguration:
    """Test cases for application configuration."""
    
    def test_app_config_in_testing_mode(self, client):
        """Test that app is properly configured for testing."""
        from app.app import app
        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is True
    
    def test_logging_configuration(self):
        """Test that logging is properly configured."""
        from logging_config import get_logger
        
        logger = get_logger('test')
        assert logger is not None
        assert logger.name == 'sentiment_analyzer.test'
