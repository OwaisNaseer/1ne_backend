"""
Comprehensive API endpoint testing script.
Run this after starting the server: uvicorn app.main:app --reload
"""
import requests
import json
import sys
import time
import os
from typing import Dict, Any, List, Tuple

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Set encoding to UTF-8 to prevent issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} - {test_name}")
    if details:
        print(f"       {details}")

def test_health() -> Tuple[bool, str]:
    """Test health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Status: {data.get('status')}"
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_list_templates() -> Tuple[bool, str]:
    """Test list templates endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/templates", timeout=10)
        if response.status_code == 200:
            templates = response.json()
            count = len(templates)
            if count > 0:
                first_slug = templates[0].get('slug', 'N/A')
                return True, f"Found {count} templates. First: {first_slug}"
            return True, f"Found {count} templates (database may need seeding)"
        return False, f"Status code: {response.status_code}, Response: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_get_template_detail(slug: str = "lesson_planner") -> Tuple[bool, str]:
    """Test get template detail endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/templates/{slug}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, f"Template: {data.get('name', 'N/A')}, Version: {data.get('latest_version', {}).get('version', 'N/A')}"
        elif response.status_code == 404:
            return False, f"Template '{slug}' not found (may need to seed database)"
        return False, f"Status code: {response.status_code}, Response: {response.text[:100]}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_execute_non_streaming(slug: str = "lesson_planner") -> Tuple[bool, str]:
    """Test non-streaming template execution."""
    payload = {
        "data": {
            "subject": "science",
            "grade": 5,
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand how Earth's rotation causes day and night.",
            "time_duration": "45 min",
            "bloom_level": "Understand",
            "differentiation_needs": False
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/templates/{slug}/execute",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            details = f"Execution ID: {data.get('execution_id', 'N/A')[:8]}..., Model: {data.get('model_used', 'N/A')}, Provider: {data.get('provider_used', 'N/A')}"
            has_output = bool(data.get('output'))
            if has_output:
                details += ", Output: ✓"
            return True, details
        elif response.status_code == 404:
            return False, f"Template '{slug}' not found or no published version"
        else:
            return False, f"Status code: {response.status_code}, Response: {response.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Request timed out (may be waiting for LLM response)"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_execute_streaming(slug: str = "lesson_planner") -> Tuple[bool, str]:
    """Test streaming template execution."""
    payload = {
        "data": {
            "subject": "science",
            "grade": 5,
            "topic": "Earth's Rotation",
            "learning_objective": "Students will understand how Earth's rotation causes day and night.",
            "time_duration": "45 min",
            "bloom_level": "Understand",
            "differentiation_needs": False
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/templates/{slug}/execute-stream",
            json=payload,
            stream=True,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'text/event-stream' in content_type:
                events = []
                start_time = time.time()
                
                for line in response.iter_lines():
                    if time.time() - start_time > TIMEOUT:
                        return False, "Stream timeout exceeded"
                    
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                event_data = json.loads(line_str[6:])
                                events.append(event_data)
                                event_type = event_data.get('type', 'unknown')
                                
                                if event_type == 'done':
                                    exec_id = event_data.get('execution_id', 'N/A')
                                    return True, f"Received {len(events)} events, Execution ID: {exec_id[:8]}..., Content-Type: SSE"
                                elif event_type == 'error':
                                    error_msg = event_data.get('message', 'Unknown error')
                                    return False, f"Stream error: {error_msg}"
                            except json.JSONDecodeError:
                                continue
                
                if events:
                    return True, f"Received {len(events)} events (no 'done' event, may still be streaming)"
                return False, "No events received"
            else:
                return False, f"Wrong content-type: {content_type}"
        elif response.status_code == 404:
            return False, f"Template '{slug}' not found or no published version"
        else:
            return False, f"Status code: {response.status_code}, Response: {response.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Run all tests."""
    print_header("1ne.ai Backend - API Endpoint Test Report")
    
    # Check if server is running
    print("\nChecking if server is running...")
    health_passed, health_details = test_health()
    print_result("Server Health Check", health_passed, health_details)
    
    if not health_passed:
        print("\n[ERROR] Server is not running or not accessible!")
        print("   Please start the server with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    print("\n[OK] Server is running. Starting endpoint tests...\n")
    
    results = []
    
    # Test 1: List Templates
    print("1. Testing List Templates endpoint...")
    passed, details = test_list_templates()
    print_result("List Templates", passed, details)
    results.append(("List Templates", passed))
    time.sleep(1)
    
    # Test 2: Get Template Detail
    print("\n2. Testing Get Template Detail endpoint...")
    passed, details = test_get_template_detail()
    print_result("Get Template Detail", passed, details)
    results.append(("Get Template Detail", passed))
    time.sleep(1)
    
    # Test 3: Non-Streaming Execution
    print("\n3. Testing Non-Streaming Execution endpoint...")
    print("   (This may take 10-30 seconds if using real LLM)")
    passed, details = test_execute_non_streaming()
    print_result("Non-Streaming Execution", passed, details)
    results.append(("Non-Streaming Execution", passed))
    time.sleep(2)
    
    # Test 4: Streaming Execution
    print("\n4. Testing Streaming Execution endpoint...")
    print("   (This may take 10-30 seconds if using real LLM)")
    passed, details = test_execute_streaming()
    print_result("Streaming Execution", passed, details)
    results.append(("Streaming Execution", passed))
    
    # Summary
    print_header("Test Summary")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print(f"\n[WARNING] {total_count - passed_count} test(s) failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

