"""
Quick script to check if backend is running and accessible.
"""
import sys
import requests
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"

def check_backend():
    """Check if backend is running and accessible."""
    print("Checking backend server...")
    print(f"Base URL: {BASE_URL}\n")
    
    # Check health endpoint
    try:
        health_url = urljoin(BASE_URL, "/health")
        print(f"1. Checking health endpoint: {health_url}")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
        else:
            print(f"   ❌ Health check failed: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to backend at {BASE_URL}")
        print("   → Backend server is not running!")
        print("   → Start it with: uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Check templates endpoint
    try:
        templates_url = urljoin(BASE_URL, "/api/v1/templates")
        print(f"\n2. Checking templates endpoint: {templates_url}")
        response = requests.get(templates_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print(f"   ✅ Templates endpoint working: {count} templates found")
        else:
            print(f"   ⚠️  Templates endpoint returned: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to templates endpoint")
        return False
    except Exception as e:
        print(f"   ⚠️  Error checking templates: {e}")
    
    # Check CORS headers
    try:
        print(f"\n3. Checking CORS configuration...")
        response = requests.options(
            urljoin(BASE_URL, "/api/v1/templates"),
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
            timeout=5
        )
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
        }
        if cors_headers["access-control-allow-origin"]:
            print(f"   ✅ CORS configured: {cors_headers}")
        else:
            print(f"   ⚠️  CORS headers not found - may cause frontend issues")
    except Exception as e:
        print(f"   ⚠️  Could not check CORS: {e}")
    
    print("\n✅ Backend is running and accessible!")
    return True

if __name__ == "__main__":
    success = check_backend()
    sys.exit(0 if success else 1)

