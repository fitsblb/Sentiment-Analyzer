"""
End-to-end API tests that simulate real-world usage scenarios.
These tests run against the actual API endpoints without mocking.
"""
import pytest
import requests
import time
import json
import threading
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import TestConfig


class TestLiveAPIEndpoints:
    """
    Live API tests that require the Flask application to be running.
    These tests should be run when the development server is active.
    """
    
    BASE_URL = "http://127.0.0.1:5000"
    
    @classmethod
    def setup_class(cls):
        """Check if the API server is running before running tests."""
        try:
            response = requests.get(f"{cls.BASE_URL}/api/health", timeout=2)
            if response.status_code != 200:
                pytest.skip("API server is not running or not healthy")
        except requests.exceptions.ConnectionError:
            pytest.skip("API server is not running")
    
    def test_health_endpoint_live(self):
        """Test the live health endpoint."""
        response = requests.get(f"{self.BASE_URL}/api/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'healthy'
        assert 'model' in data
        assert 'timestamp' in data
        assert 'version' in data
    
    def test_info_endpoint_live(self):
        """Test the live info endpoint."""
        response = requests.get(f"{self.BASE_URL}/api/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['name'] == 'Sentiment Analyzer API'
        assert 'endpoints' in data
        assert 'limits' in data
    
    def test_sentiment_analysis_positive(self):
        """Test sentiment analysis with clearly positive text."""
        test_cases = [
            "This product is absolutely amazing!",
            "I love this restaurant, best food ever!",
            "Excellent service and wonderful experience!",
            "Perfect quality, highly recommended!"
        ]
        
        for text in test_cases:
            response = requests.post(f"{self.BASE_URL}/api/analyze",
                                   json={'text': text},
                                   headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['sentiment'] == 'Positive'
            assert data['confidence'] > 0.5  # Should be confident
            assert data['text_length'] == len(text)
            assert 'processing_time' in data
    
    def test_sentiment_analysis_negative(self):
        """Test sentiment analysis with clearly negative text."""
        test_cases = [
            "This product is terrible and broken!",
            "Worst service I've ever experienced.",
            "Complete waste of money, very disappointed.",
            "Awful quality, would not recommend."
        ]
        
        for text in test_cases:
            response = requests.post(f"{self.BASE_URL}/api/analyze",
                                   json={'text': text},
                                   headers={'Content-Type': 'application/json'})
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['sentiment'] == 'Negative'
            assert data['confidence'] > 0.5  # Should be confident
            assert data['text_length'] == len(text)
    
    def test_api_performance_benchmark(self):
        """Test API performance with multiple requests."""
        test_text = "This is a performance test for the sentiment analyzer."
        
        response_times = []
        
        # Make 10 requests and measure response times
        for i in range(10):
            start_time = time.time()
            response = requests.post(f"{self.BASE_URL}/api/analyze",
                                   json={'text': test_text},
                                   headers={'Content-Type': 'application/json'})
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            response_times.append(response_time)
        
        # Performance assertions
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Max response time: {max_response_time:.3f}s")
        
        # API should respond within reasonable time limits
        assert avg_response_time < TestConfig.EXPECTED_RESPONSE_TIME
        assert max_response_time < TestConfig.EXPECTED_RESPONSE_TIME * 2
    
    def test_concurrent_requests(self):
        """Test API behavior under concurrent load."""
        test_text = "Concurrent request test for sentiment analysis."
        num_threads = 5
        results = []
        errors = []
        
        def make_request():
            try:
                response = requests.post(f"{self.BASE_URL}/api/analyze",
                                       json={'text': test_text},
                                       headers={'Content-Type': 'application/json'},
                                       timeout=TestConfig.API_TIMEOUT)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create and start threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == num_threads
        assert all(status == 200 for status in results)
    
    def test_error_responses_live(self):
        """Test live error response handling."""
        # Test empty text
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               json={'text': ''},
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        
        # Test missing text field
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               json={},
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        
        # Test text too long
        long_text = "x" * 1001
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               json={'text': long_text},
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
        
        # Test non-JSON content
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               data="not json",
                               headers={'Content-Type': 'text/plain'})
        assert response.status_code == 400


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    BASE_URL = "http://127.0.0.1:5000"
    
    @classmethod
    def setup_class(cls):
        """Check if the API server is running."""
        try:
            response = requests.get(f"{cls.BASE_URL}/api/health", timeout=2)
            if response.status_code != 200:
                pytest.skip("API server is not running")
        except requests.exceptions.ConnectionError:
            pytest.skip("API server is not running")
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        test_cases = [
            "Great product! 🚀😊👍",  # Emojis
            "Café is très bon! 🇫🇷",  # Accented characters
            "这个产品很好！",  # Chinese characters
            "منتج رائع!",  # Arabic characters
            "Отличный продукт!",  # Cyrillic characters
            "Special chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`",  # Special symbols
        ]
        
        for text in test_cases:
            response = requests.post(f"{self.BASE_URL}/api/analyze",
                                   json={'text': text},
                                   headers={'Content-Type': 'application/json'})
            
            # Should handle gracefully (200) or fail gracefully (400)
            assert response.status_code in [200, 400]
            
            if response.status_code == 200:
                data = response.json()
                assert 'sentiment' in data
                assert 'confidence' in data
    
    def test_boundary_text_lengths(self):
        """Test text at boundary lengths."""
        # Test minimum valid length (3 characters)
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               json={'text': 'abc'},
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        # Test maximum valid length (1000 characters)
        max_text = "a" * 1000
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               json={'text': max_text},
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        
        # Test just over maximum (1001 characters)
        over_max_text = "a" * 1001
        response = requests.post(f"{self.BASE_URL}/api/analyze",
                               json={'text': over_max_text},
                               headers={'Content-Type': 'application/json'})
        assert response.status_code == 400
    
    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        test_cases = [
            "   Leading spaces",
            "Trailing spaces   ",
            "   Both sides   ",
            "Multiple\n\nlines\n\nof\n\ntext",
            "Tabs\t\tand\t\tspaces",
            "Mixed   \t\n  whitespace",
        ]
        
        for text in test_cases:
            response = requests.post(f"{self.BASE_URL}/api/analyze",
                                   json={'text': text},
                                   headers={'Content-Type': 'application/json'})
            
            # Should handle all whitespace scenarios
            assert response.status_code == 200
            data = response.json()
            assert 'sentiment' in data


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_api_live.py -v
    pytest.main([__file__, "-v"])
