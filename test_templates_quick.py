"""Quick test to verify templates API works."""
import requests
import sys
import signal

BASE_URL = "http://localhost:8000"
TIMEOUT = 3  # 3 seconds max

def timeout_handler(signum, frame):
    raise TimeoutError("Test timed out")

def test_templates():
    """Test templates listing endpoint."""
    print("=" * 60)
    print("Testing Templates API (Quick Test)")
    print("=" * 60)
    
    try:
        # Test health first with short timeout
        print("\n1. Testing health endpoint...")
        try:
            health = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if health.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print(f"   ❌ Health check failed: {health.status_code}")
                return False
        except requests.exceptions.Timeout:
            print("   ❌ Health check timed out - backend may not be running")
            return False
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect - backend is not running")
            print("   💡 Start backend: uvicorn app.main:app --reload")
            return False
        
        # Test templates endpoint with short timeout
        print("\n2. Testing templates endpoint...")
        try:
            response = requests.get(f"{BASE_URL}/api/v1/templates", timeout=TIMEOUT)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                templates = response.json()
                count = len(templates) if isinstance(templates, list) else 0
                print(f"   ✅ Templates endpoint working")
                print(f"   📊 Found {count} templates")
                
                if count > 0:
                    print("\n   First template:")
                    first = templates[0]
                    print(f"   - ID: {first.get('id', 'N/A')}")
                    print(f"   - Name: {first.get('name', 'N/A')}")
                    print(f"   - Slug: {first.get('slug', 'N/A')}")
                    print(f"   - Category: {first.get('category', 'N/A')}")
                    print(f"   - Subject: {first.get('subject_default', 'N/A')}")
                    return True
                else:
                    print("   ⚠️  No templates found (database may be empty)")
                    print("   💡 Run: python -m app.seed.cli")
                    return True  # Endpoint works, just no data
            else:
                print(f"   ❌ Templates endpoint failed")
                print(f"   Response: {response.text[:200]}")
                return False
        except requests.exceptions.Timeout:
            print("   ❌ Templates request timed out (backend may be slow)")
            print("   💡 Check backend logs for database connection issues")
            return False
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to templates endpoint")
            return False
            
    except KeyboardInterrupt:
        print("\n   ⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    # Set timeout for entire script
    if sys.platform != 'win32':
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second total timeout
    
    try:
        success = test_templates()
        print("\n" + "=" * 60)
        if success:
            print("✅ Test completed - Templates API is working!")
        else:
            print("❌ Test failed - Check the errors above")
        print("=" * 60)
    except TimeoutError:
        print("\n❌ Test timed out - backend may be hanging")
        print("💡 Check backend server and database connection")
    finally:
        if sys.platform != 'win32':
            signal.alarm(0)  # Cancel alarm

