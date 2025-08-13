#!/usr/bin/env python3
"""
Test runner script for the Sentiment Analyzer project.
Provides easy commands to run different types of tests.
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n🔄 {description}")
    print("=" * 60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ FAILED")
        if result.stderr:
            print("Error:", result.stderr)
        if result.stdout:
            print("Output:", result.stdout)
    
    return result.returncode == 0


def check_server_running():
    """Check if the Flask development server is running."""
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("""
🧪 Sentiment Analyzer Test Runner

Usage: python run_tests.py <command>

Available commands:
  unit        - Run unit tests only
  integration - Run integration tests only  
  api         - Run API tests (requires server to be running)
  live        - Run live API tests (requires server to be running)
  all         - Run all tests except live tests
  coverage    - Run tests with coverage report
  quick       - Run a quick subset of tests
  
Examples:
  python run_tests.py unit
  python run_tests.py coverage
  python run_tests.py all
        """)
        return
    
    command = sys.argv[1].lower()
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    if command == "unit":
        print("🧪 Running Unit Tests")
        run_command("python -m pytest tests/test_model.py -v", "Unit Tests (Model)")
        
    elif command == "integration":
        print("🔧 Running Integration Tests")
        run_command("python -m pytest tests/test_app.py -v", "Integration Tests (Flask App)")
        
    elif command == "api" or command == "live":
        print("🌐 Running Live API Tests")
        if not check_server_running():
            print("❌ Error: Flask server is not running!")
            print("Please start the server first: python app/app.py")
            return
        
        run_command("python -m pytest tests/test_api_live.py -v", "Live API Tests")
        
    elif command == "all":
        print("🚀 Running All Tests (except live)")
        success = True
        success &= run_command("python -m pytest tests/test_model.py -v", "Unit Tests")
        success &= run_command("python -m pytest tests/test_app.py -v", "Integration Tests")
        
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
    elif command == "coverage":
        print("📊 Running Tests with Coverage")
        run_command("python -m pytest tests/ --cov=app --cov=config --cov=logging_config --cov-report=html --cov-report=term", 
                   "Coverage Analysis")
        print("\n📈 Coverage report generated in htmlcov/index.html")
        
    elif command == "quick":
        print("⚡ Running Quick Test Suite")
        run_command("python -m pytest tests/test_model.py::TestSentimentAnalyzer::test_sentiment_label_mapping_original_model -v", 
                   "Quick Model Test")
        run_command("python -m pytest tests/test_app.py::TestAPIEndpoints::test_health_endpoint -v", 
                   "Quick API Test")
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python run_tests.py' without arguments to see available commands.")


if __name__ == "__main__":
    main()
