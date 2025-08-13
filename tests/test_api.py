#!/usr/bin/env python3
"""
API Testing Script for Sentiment Analyzer
This script demonstrates how to interact with all the API endpoints.
"""

import requests
import json
import time
from typing import Dict, Any


class SentimentAnalyzerAPITester:
    """Test client for the Sentiment Analyzer API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SentimentAnalyzer-APITester/1.0'
        })
    
    def test_health_endpoint(self) -> Dict[str, Any]:
        """Test the health check endpoint."""
        print("🔍 Testing Health Endpoint...")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def test_info_endpoint(self) -> Dict[str, Any]:
        """Test the API info endpoint."""
        print("\n📋 Testing Info Endpoint...")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/info")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def test_analyze_endpoint(self, text: str) -> Dict[str, Any]:
        """Test the sentiment analysis endpoint."""
        print(f"\n🧠 Testing Analysis Endpoint with: '{text}'")
        print("=" * 50)
        
        payload = {"text": text}
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/analyze", 
                json=payload
            )
            end_time = time.time()
            
            print(f"Status Code: {response.status_code}")
            print(f"Request took: {end_time - start_time:.3f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Pretty print the results
                sentiment = result.get('sentiment', 'Unknown')
                confidence = result.get('confidence', 0)
                print(f"\n✨ Result: {sentiment} ({confidence*100:.1f}% confident)")
                
                return result
            else:
                print(f"❌ Error Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def test_error_handling(self):
        """Test API error handling with invalid inputs."""
        print("\n🚨 Testing Error Handling...")
        print("=" * 50)
        
        # Test empty text
        print("Testing empty text...")
        self.test_analyze_endpoint("")
        
        # Test very long text
        print("\nTesting very long text...")
        long_text = "This is a test. " * 100  # 1600+ characters
        self.test_analyze_endpoint(long_text)
        
        # Test non-JSON request
        print("\nTesting invalid JSON...")
        try:
            response = self.session.post(
                f"{self.base_url}/api/analyze",
                data="invalid json"
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_comprehensive_test(self):
        """Run all API tests."""
        print("🚀 Starting Comprehensive API Testing")
        print("=" * 60)
        
        # Test basic endpoints
        self.test_health_endpoint()
        self.test_info_endpoint()
        
        # Test different sentiment examples
        test_cases = [
            "This restaurant has amazing food and excellent service!",
            "The movie was okay, nothing special but not terrible either.",
            "Terrible customer service and the food was cold.",
            "I absolutely love this product! Best purchase ever!",
            "The weather is nice today.",
            "This is a very short text.",
        ]
        
        for text in test_cases:
            self.test_analyze_endpoint(text)
        
        # Test error cases
        self.test_error_handling()
        
        print("\n✅ API Testing Complete!")


def main():
    """Main function to run the API tests."""
    tester = SentimentAnalyzerAPITester()
    
    print("🎯 Sentiment Analyzer API Tester")
    print("Make sure your Flask app is running on http://127.0.0.1:5000")
    print()
    
    # Quick connectivity test
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is reachable!")
            tester.run_comprehensive_test()
        else:
            print("❌ API returned non-200 status. Is the server running?")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
