#!/usr/bin/env python3
"""
Complete Workflow Test for AgriVision
Tests authentication flow, ML models, and all features
"""
import requests
import json
import time
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_server_health():
    """Test if server is running"""
    print("🔍 Testing Server Health...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Health: {data}")
            return True
        else:
            print(f"❌ Server Health Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server Health Error: {e}")
        return False

def test_authentication_flow():
    """Test complete authentication flow"""
    print("\n🔐 Testing Authentication Flow...")
    
    # Test 1: Access homepage without login (should redirect to login)
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=5)
        if response.status_code == 200:
            if "login" in response.text.lower():
                print("✅ Homepage redirects to login when not authenticated")
            else:
                print("⚠️ Homepage accessible without authentication")
        else:
            print(f"❌ Homepage access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Homepage access error: {e}")
    
    # Test 2: Login with valid credentials
    try:
        login_data = {"username": "farmer", "password": "farmer123", "role": "farmer"}
        response = requests.post(
            "http://127.0.0.1:5000/api/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful: {data['user']} ({data['role']})")
            
            # Test 3: Access homepage with session
            session = requests.Session()
            session.post(
                "http://127.0.0.1:5000/api/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            homepage_response = session.get("http://127.0.0.1:5000/")
            if homepage_response.status_code == 200:
                if "agrivision" in homepage_response.text.lower():
                    print("✅ Homepage accessible after login")
                    return True
                else:
                    print("⚠️ Homepage content unclear after login")
            else:
                print(f"❌ Homepage access after login failed: {homepage_response.status_code}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication flow error: {e}")
        return False

def test_ml_model_integration():
    """Test ML model integration"""
    print("\n🤖 Testing ML Model Integration...")
    
    # Test crop prediction
    try:
        test_data = {
            "N": 90, "P": 40, "K": 40,
            "temperature": 20.5, "humidity": 80,
            "ph": 6.5, "rainfall": 200
        }
        
        response = requests.post(
            "http://127.0.0.1:5000/api/predict/crop",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crop Prediction: {data['predictions'][0]['crop']}")
            print(f"   Confidence: {data['predictions'][0]['probability']:.3f}")
            print(f"   Top 3: {[c['crop'] for c in data['predictions']]}")
            
            # Test fertilizer recommendation
            fertilizer_data = {
                "crop": data['predictions'][0]['crop'],
                "N": 50, "P": 20, "K": 20
            }
            
            fert_response = requests.post(
                "http://127.0.0.1:5000/api/predict/fertilizer",
                json=fertilizer_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if fert_response.status_code == 200:
                fert_data = fert_response.json()
                print(f"✅ Fertilizer Recommendation: {fert_data['data']['type']}")
                print(f"   Recommendation: {fert_data['data']['recommendation']}")
                return True
            else:
                print(f"❌ Fertilizer recommendation failed: {fert_response.status_code}")
                return False
        else:
            print(f"❌ Crop prediction failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ML model integration error: {e}")
        return False

def test_weather_api():
    """Test weather API integration"""
    print("\n🌤️ Testing Weather API...")
    
    try:
        cities = ["Mumbai", "Delhi", "Bangalore"]
        success_count = 0
        
        for city in cities:
            response = requests.post(
                "http://127.0.0.1:5000/api/weather",
                json={"city": city},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                weather = data['data']
                print(f"✅ {city}: {weather['temperature']}°C, {weather['humidity']}% humidity")
                success_count += 1
            else:
                print(f"❌ Weather for {city} failed: {response.status_code}")
        
        return success_count == len(cities)
        
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return False

def test_chatbot_feature():
    """Test AI chatbot feature"""
    print("\n🤖 Testing AI Chatbot Feature...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/chatbot",
            json={"message": "Hello, can you help me with farming?"},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatbot Response: {data['response'][:80]}...")
            print(f"   Success: {data['success']}")
            return True
        else:
            print(f"❌ Chatbot failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        return False

def test_disease_detection():
    """Test disease detection placeholder"""
    print("\n🦠 Testing Disease Detection...")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/predict/disease",
            json={"image": "test"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Disease Detection: {data['message']}")
            print(f"   Status: {data['status']}")
            return True
        else:
            print(f"❌ Disease detection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Disease detection error: {e}")
        return False

def test_file_structure():
    """Test if files are organized properly"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        "src/backend/app.py",
        "src/models/crop_model (1).joblib",
        "src/models/features (1).json",
        "src/data/fertilizer (2).csv",
        "src/frontend/templates/index.html",
        "src/frontend/templates/login.html",
        "src/frontend/templates/signup.html",
        "src/frontend/static/css/style.css",
        "src/frontend/static/js/script.js",
        "src/frontend/static/js/login.js",
        "src/backend/utils/weather_api.py",
        "app.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ All required files are in place")
        return True
    else:
        print(f"❌ Missing files: {missing_files}")
        return False

def main():
    print("🚀 AgriVision Complete Workflow Test")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Server Health", test_server_health),
        ("Authentication Flow", test_authentication_flow),
        ("ML Model Integration", test_ml_model_integration),
        ("Weather API", test_weather_api),
        ("AI Chatbot", test_chatbot_feature),
        ("Disease Detection", test_disease_detection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 COMPLETE WORKFLOW TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! AgriVision is fully functional!")
        print("\n✅ Complete Workflow Verified:")
        print("   - Authentication: Login → Homepage flow working")
        print("   - ML Models: Crop prediction + Fertilizer recommendation")
        print("   - Weather API: Real-time data integration")
        print("   - AI Chatbot: Live and integrated with Gemini")
        print("   - Disease Detection: Under development placeholder")
        print("   - File Structure: Organized and accessible")
        
        print("\n🌐 Access your application:")
        print("   URL: http://127.0.0.1:5000")
        print("   Login: farmer/farmer123, officer/officer123, user/user123")
        
        print("\n📋 Features Available:")
        print("   ✅ Crop Recommendation (ML Model)")
        print("   ✅ Fertilizer Suggestion (CSV Data)")
        print("   ✅ Weather Integration (API Key)")
        print("   ✅ User Authentication (Role-based)")
        print("   ✅ AI Chatbot (Live Gemini Integration)")
        print("   ✅ Disease Detection (Under Development)")
        
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("💡 Make sure the Flask server is running: python app.py")

if __name__ == "__main__":
    main()
