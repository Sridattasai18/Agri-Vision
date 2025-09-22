#!/usr/bin/env python3
"""
API Tests for Crop Recommendation System
"""
import requests
import json
import time

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["model_loaded"] == True
        print("✅ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_meta_endpoint():
    """Test metadata endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/meta", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "classes" in data
        assert len(data["features"]) == 7
        print("✅ Meta endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Meta endpoint test failed: {e}")
        return False

def test_prediction_endpoint():
    """Test prediction endpoint"""
    try:
        test_data = {
            "N": 90, "P": 40, "K": 40,
            "temperature": 20.5, "humidity": 80,
            "ph": 6.5, "rainfall": 200
        }
        
        response = requests.post(
            "http://127.0.0.1:5000/predict?top_k=3",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert len(data["predictions"]) == 3
        assert "crop" in data["predictions"][0]
        assert "probability" in data["predictions"][0]
        print("✅ Prediction endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Prediction endpoint test failed: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🧪 Running API Tests...")
    print("=" * 40)
    
    tests = [
        test_health_endpoint,
        test_meta_endpoint,
        test_prediction_endpoint
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    run_all_tests()
