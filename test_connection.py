#!/usr/bin/env python3
"""Quick connection test - no hanging"""
import requests
import sys

def test_backend():
    """Test backend connection with timeout"""
    try:
        # Test 1: Health endpoint
        print("🔵 Testing /health endpoint...")
        r = requests.get("http://localhost:8000/health", timeout=2)
        print(f"✅ Health: {r.status_code} - {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health failed: {e}")
        return False
    
    try:
        # Test 2: Test endpoint
        print("🔵 Testing /api/v1/test endpoint...")
        r = requests.get("http://localhost:8000/api/v1/test", timeout=2)
        print(f"✅ Test: {r.status_code} - {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Test endpoint failed: {e}")
        return False
    
    try:
        # Test 3: Templates endpoint
        print("🔵 Testing /api/v1/templates endpoint...")
        r = requests.get("http://localhost:8000/api/v1/templates", timeout=2)
        print(f"✅ Templates: {r.status_code}")
        data = r.json()
        if isinstance(data, list):
            print(f"✅ Found {len(data)} templates")
            if data:
                print(f"✅ First template: {data[0].get('name', 'N/A')}")
        else:
            print(f"⚠️ Response is not a list: {type(data)}")
    except requests.exceptions.Timeout:
        print("❌ Templates endpoint TIMEOUT after 2 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Templates failed: {e}")
        return False
    
    print("\n✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1)





