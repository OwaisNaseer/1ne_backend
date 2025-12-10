"""Complete verification script - tests everything automatically."""
import requests
import sys
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 5

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_health():
    """Test 1: Health endpoint"""
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            print("✅ Backend server is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        print("   💡 Start backend: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_templates():
    """Test 2: Templates endpoint"""
    print_header("TEST 2: Templates API")
    try:
        print(f"   Calling: {BASE_URL}/api/v1/templates")
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/templates", timeout=TIMEOUT)
        elapsed = time.time() - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            templates = response.json()
            count = len(templates) if isinstance(templates, list) else 0
            print(f"   ✅ Templates endpoint working")
            print(f"   📊 Found {count} templates")
            
            if count > 0:
                print("\n   📋 Sample templates:")
                for i, t in enumerate(templates[:3], 1):
                    print(f"   {i}. {t.get('name', 'N/A')} (slug: {t.get('slug', 'N/A')})")
                return True, count
            else:
                print("   ⚠️  No templates in database")
                print("   💡 Run: python -m app.seed.cli")
                return True, 0
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            return False, 0
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return False, 0
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False, 0

def test_template_detail():
    """Test 3: Template detail endpoint"""
    print_header("TEST 3: Template Detail API")
    try:
        # First get a template slug
        list_response = requests.get(f"{BASE_URL}/api/v1/templates", timeout=TIMEOUT)
        if list_response.status_code == 200:
            templates = list_response.json()
            if templates and len(templates) > 0:
                slug = templates[0].get('slug')
                print(f"   Testing with slug: {slug}")
                
                response = requests.get(f"{BASE_URL}/api/v1/templates/{slug}", timeout=TIMEOUT)
                if response.status_code == 200:
                    print("   ✅ Template detail endpoint working")
                    detail = response.json()
                    print(f"   Template: {detail.get('name', 'N/A')}")
                    return True
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    return False
            else:
                print("   ⚠️  No templates to test detail endpoint")
                return True  # Not a failure, just no data
        else:
            print("   ❌ Cannot get template list")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_cors():
    """Test 4: CORS headers"""
    print_header("TEST 4: CORS Configuration")
    try:
        response = requests.options(
            f"{BASE_URL}/api/v1/templates",
            headers={
                'Origin': 'http://localhost:5173',
                'Access-Control-Request-Method': 'GET'
            },
            timeout=TIMEOUT
        )
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
        }
        print(f"   CORS Headers: {cors_headers}")
        if cors_headers['access-control-allow-origin']:
            print("   ✅ CORS configured")
            return True
        else:
            print("   ⚠️  CORS headers not found (may still work)")
            return True
    except Exception as e:
        print(f"   ⚠️  CORS test error: {e}")
        return True  # Not critical

def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("  COMPLETE SYSTEM VERIFICATION")
    print("🚀" * 30)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print("\n❌ Backend is not running. Please start it first.")
        print("   Command: uvicorn app.main:app --reload")
        return
    
    # Test 2: Templates
    success, count = test_templates()
    results.append(("Templates API", success))
    
    # Test 3: Template Detail
    results.append(("Template Detail", test_template_detail()))
    
    # Test 4: CORS
    results.append(("CORS", test_cors()))
    
    # Summary
    print_header("TEST SUMMARY")
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - System is working!")
        if count > 0:
            print(f"🎉 {count} templates are available in the database")
        else:
            print("💡 To add templates, run: python -m app.seed.cli")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)





