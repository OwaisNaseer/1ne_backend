"""
Complete endpoint testing - tests all endpoints and reports results.
"""
import requests
import json
import sys
import time

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"
TIMEOUT = 60

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_result(test_name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} - {test_name}")
    if details:
        print(f"        {details}")

def test_health():
    """Test 1: Health Check"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return True, f"Status: {data.get('status')}"
        return False, f"Status code: {r.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def test_list_templates():
    """Test 2: List Templates"""
    try:
        r = requests.get(f"{BASE_URL}/api/v1/templates", timeout=10)
        if r.status_code == 200:
            templates = r.json()
            count = len(templates)
            if count > 0:
                return True, f"Found {count} templates. First: {templates[0].get('slug', 'N/A')}"
            return True, f"Found {count} templates (empty - database needs seeding)"
        elif r.status_code == 500:
            error_detail = r.text[:200] if r.text else "Internal server error"
            return False, f"Database error: {error_detail}"
        return False, f"Status: {r.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def test_get_template_detail(slug="lesson_planner"):
    """Test 3: Get Template Detail"""
    try:
        r = requests.get(f"{BASE_URL}/api/v1/templates/{slug}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return True, f"Template: {data.get('name', 'N/A')}, Version: {data.get('latest_version', {}).get('version', 'N/A') if data.get('latest_version') else 'N/A'}"
        elif r.status_code == 404:
            return False, f"Template '{slug}' not found (database needs seeding)"
        elif r.status_code == 500:
            return False, f"Database error: {r.text[:200] if r.text else 'Internal error'}"
        return False, f"Status: {r.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def test_execute_non_streaming(slug="lesson_planner"):
    """Test 4: Non-Streaming Execution"""
    payload = {
        "data": {
            "subject": "science",
            "grade": 5,
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration": "45 min",
            "bloom_level": "Understand",
            "differentiation_needs": False
        }
    }
    
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/templates/{slug}/execute",
            json=payload,
            timeout=TIMEOUT
        )
        
        if r.status_code == 200:
            data = r.json()
            exec_id = str(data.get('execution_id', 'N/A'))[:8]
            model = data.get('model_used', 'N/A')
            provider = data.get('provider_used', 'N/A')
            has_output = bool(data.get('output'))
            return True, f"Execution ID: {exec_id}..., Model: {model}, Provider: {provider}, Has Output: {has_output}"
        elif r.status_code == 404:
            return False, f"Template '{slug}' not found (database needs seeding)"
        elif r.status_code == 500:
            return False, f"Database/LLM error: {r.text[:200] if r.text else 'Internal error'}"
        return False, f"Status: {r.status_code}, Response: {r.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Request timed out (may be waiting for LLM)"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def test_execute_streaming(slug="lesson_planner"):
    """Test 5: Streaming Execution"""
    payload = {
        "data": {
            "subject": "science",
            "grade": 5,
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand rotation",
            "time_duration": "45 min",
            "bloom_level": "Understand",
            "differentiation_needs": False
        }
    }
    
    try:
        r = requests.post(
            f"{BASE_URL}/api/v1/templates/{slug}/execute-stream",
            json=payload,
            stream=True,
            timeout=TIMEOUT
        )
        
        if r.status_code == 200:
            content_type = r.headers.get('content-type', '')
            if 'text/event-stream' in content_type:
                events = []
                start_time = time.time()
                
                for line in r.iter_lines():
                    if time.time() - start_time > TIMEOUT:
                        break
                    
                    if line:
                        line_str = line.decode('utf-8', errors='replace')
                        if line_str.startswith('data: '):
                            try:
                                event_data = json.loads(line_str[6:])
                                events.append(event_data)
                                event_type = event_data.get('type', 'unknown')
                                
                                if event_type == 'done':
                                    exec_id = str(event_data.get('execution_id', 'N/A'))[:8]
                                    return True, f"Received {len(events)} events, Execution ID: {exec_id}..., SSE working"
                                elif event_type == 'error':
                                    return False, f"Stream error: {event_data.get('message', 'Unknown')[:50]}"
                            except:
                                continue
                
                if events:
                    return True, f"Received {len(events)} events (streaming working)"
                return False, "No events received"
            else:
                return False, f"Wrong content-type: {content_type}"
        elif r.status_code == 404:
            return False, f"Template '{slug}' not found (database needs seeding)"
        elif r.status_code == 500:
            return False, f"Database/LLM error: {r.text[:200] if r.text else 'Internal error'}"
        return False, f"Status: {r.status_code}"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def main():
    print_header("1ne.ai Backend - Complete Endpoint Test")
    
    # Check server
    print("\nChecking server...")
    health_passed, health_details = test_health()
    print_result("Server Health Check", health_passed, health_details)
    
    if not health_passed:
        print("\n[ERROR] Server is not running!")
        print("Start server: python -m uvicorn app.main:app --reload")
        return 1
    
    print("\n[OK] Server is running. Testing all endpoints...\n")
    
    results = []
    
    # Test 1: List Templates
    print("Test 1: List Templates")
    passed, details = test_list_templates()
    print_result("List Templates", passed, details)
    results.append(("List Templates", passed, details))
    time.sleep(1)
    
    # Test 2: Get Template Detail
    print("\nTest 2: Get Template Detail")
    passed, details = test_get_template_detail()
    print_result("Get Template Detail", passed, details)
    results.append(("Get Template Detail", passed, details))
    time.sleep(1)
    
    # Test 3: Non-Streaming Execution
    print("\nTest 3: Non-Streaming Execution")
    print("       (May take 10-30 seconds if using real LLM)")
    passed, details = test_execute_non_streaming()
    print_result("Non-Streaming Execution", passed, details)
    results.append(("Non-Streaming Execution", passed, details))
    time.sleep(2)
    
    # Test 4: Streaming Execution
    print("\nTest 4: Streaming Execution")
    print("       (May take 10-30 seconds if using real LLM)")
    passed, details = test_execute_streaming()
    print_result("Streaming Execution", passed, details)
    results.append(("Streaming Execution", passed, details))
    
    # Summary
    print_header("Test Summary")
    passed_count = sum(1 for _, p, _ in results if p)
    total_count = len(results)
    
    for test_name, passed, details in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
        if not passed and "database" in details.lower():
            print(f"        -> Database setup needed: Run 'alembic upgrade head' and 'python -m app.seed.cli'")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n[SUCCESS] All endpoints working!")
        return 0
    else:
        print(f"\n[WARNING] {total_count - passed_count} test(s) failed")
        if any("database" in d.lower() for _, _, d in results if not _):
            print("\n[INFO] Database setup required for full functionality")
        return 1

if __name__ == "__main__":
    sys.exit(main())

