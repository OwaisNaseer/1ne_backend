"""Test complete flow - backend and API"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    print("⏳ Waiting for backend server to start...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is running!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   Waiting... ({i+1}/{max_wait})")
    return False

def test_health():
    """Test 1: Health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ PASS - Health endpoint working")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ FAIL - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False

def test_templates():
    """Test 2: Templates endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Templates API")
    print("="*60)
    try:
        print(f"   Calling: {BASE_URL}/api/v1/templates")
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/templates", timeout=10)
        elapsed = time.time() - start
        
        print(f"   Status: {response.status_code}")
        print(f"   Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            templates = response.json()
            count = len(templates) if isinstance(templates, list) else 0
            print(f"✅ PASS - Templates endpoint working")
            print(f"   Found {count} templates")
            
            if count > 0:
                print(f"\n   Sample templates:")
                for i, t in enumerate(templates[:3], 1):
                    print(f"   {i}. {t.get('name', 'N/A')} (slug: {t.get('slug', 'N/A')})")
            else:
                print("   ⚠️  Database is empty - run: python -m app.seed.cli")
            return True
        else:
            print(f"❌ FAIL - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("❌ FAIL - Request timed out (backend may be hanging)")
        return False
    except Exception as e:
        print(f"❌ FAIL - Error: {e}")
        return False

def main():
    print("\n" + "🚀"*30)
    print("  COMPLETE FLOW TEST")
    print("🚀"*30)
    
    # Wait for server
    if not wait_for_server():
        print("\n❌ Backend server did not start in time")
        print("   Please start manually: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Run tests
    results = []
    results.append(("Health", test_health()))
    results.append(("Templates", test_templates()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Flow is working!")
        print("\n💡 Frontend should now be able to load templates")
        print("   Open: http://localhost:5173")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
        sys.exit(1)





