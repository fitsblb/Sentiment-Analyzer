#!/usr/bin/env python3
"""
Simple test script to validate our sentiment analyzer.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_model_import():
    """Test if we can import the model."""
    try:
        from app.model import predict, ModelError
        print("✅ Model import successful!")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_config_import():
    """Test if we can import configuration."""
    try:
        from config import config
        print("✅ Config import successful!")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_app_import():
    """Test if we can import the Flask app."""
    try:
        from app.app import app
        print("✅ App import successful!")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_basic_prediction():
    """Test basic prediction functionality."""
    try:
        from app.model import predict
        result = predict("I love this product! It's amazing!")
        print(f"✅ Basic prediction successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Basic prediction failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Basic Validation Tests")
    print("=" * 50)
    
    tests = [
        test_config_import,
        test_model_import,
        test_app_import,
        test_basic_prediction
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All basic tests passed! The sentiment analyzer is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
