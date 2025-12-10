"""
Complete end-to-end test - runs everything and reports results.
This script will NOT hang - all operations have timeouts.
"""
import requests
import json
import sys
import time
import os
import subprocess
import signal
from typing import Tuple, Optional

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
SERVER_START_TIMEOUT = 15

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

def check_server_running() -> bool:
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server() -> Optional[subprocess.Popen]:
    """Start server in background."""
    print("Starting server...")
    try:
        # Use subprocess to start server
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        # Wait for server to start
        for i in range(SERVER_START_TIMEOUT):
            time.sleep(1)
            if check_server_running():
                print(f"Server started after {i+1} seconds")
                return process
            if process.poll() is not None:
                # Process died
                stderr = process.stderr.read().decode('utf-8', errors='replace')
                print(f"Server failed to start: {stderr[:200]}")
                return None
        
        print("Server did not start in time")
        process.terminate()
        return None
    except Exception as e:
        print(f"Error starting server: {e}")
        return None

def test_health() -> Tuple[bool, str]:
    """Test health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, f"Status: {data.get('status')}"
        return False, f"Status code: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

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
            return True, f"Found {count} templates (may need seeding)"
        return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def test_execute_non_streaming(slug: str = "lesson_planner") -> Tuple[bool, str]:
    """Test non-streaming execution."""
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
        response = requests.post(
            f"{BASE_URL}/api/v1/templates/{slug}/execute",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            exec_id = str(data.get('execution_id', 'N/A'))[:8]
            return True, f"Execution ID: {exec_id}..., Model: {data.get('model_used', 'N/A')}"
        elif response.status_code == 404:
            return False, f"Template '{slug}' not found (may need seeding)"
        else:
            return False, f"Status: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def test_execute_streaming(slug: str = "lesson_planner") -> Tuple[bool, str]:
    """Test streaming execution."""
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
        response = requests.post(
            f"{BASE_URL}/api/v1/templates/{slug}/execute-stream",
            json=payload,
            stream=True,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            events = []
            start_time = time.time()
            
            for line in response.iter_lines():
                if time.time() - start_time > TIMEOUT:
                    break
                
                if line:
                    line_str = line.decode('utf-8', errors='replace')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])
                            events.append(event_data)
                            if event_data.get('type') == 'done':
                                return True, f"Received {len(events)} events, Execution ID: {str(event_data.get('execution_id', 'N/A'))[:8]}..."
                            elif event_data.get('type') == 'error':
                                return False, f"Stream error: {event_data.get('message', 'Unknown')[:50]}"
                        except:
                            continue
            
            if events:
                return True, f"Received {len(events)} events"
            return False, "No events received"
        elif response.status_code == 404:
            return False, f"Template '{slug}' not found"
        else:
            return False, f"Status: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def main():
    """Run complete test suite."""
    print_header("1ne.ai Backend - Complete End-to-End Test")
    
    # Check if server is already running
    if check_server_running():
        print("[INFO] Server is already running")
        server_process = None
    else:
        # Try to start server
        server_process = start_server()
        if not server_process:
            print("\n[ERROR] Could not start server")
            print("Please start server manually: python -m uvicorn app.main:app --reload")
            return 1
        time.sleep(2)
    
    try:
        results = []
        
        # Test 1: Health
        print("\n1. Testing Health endpoint...")
        passed, details = test_health()
        print_result("Health Check", passed, details)
        results.append(("Health Check", passed))
        
        if not passed:
            print("\n[ERROR] Server health check failed. Stopping tests.")
            return 1
        
        time.sleep(1)
        
        # Test 2: List Templates
        print("\n2. Testing List Templates endpoint...")
        passed, details = test_list_templates()
        print_result("List Templates", passed, details)
        results.append(("List Templates", passed))
        time.sleep(1)
        
        # Test 3: Non-Streaming
        print("\n3. Testing Non-Streaming Execution...")
        print("   (May take 10-30 seconds)")
        passed, details = test_execute_non_streaming()
        print_result("Non-Streaming Execution", passed, details)
        results.append(("Non-Streaming Execution", passed))
        time.sleep(2)
        
        # Test 4: Streaming
        print("\n4. Testing Streaming Execution...")
        print("   (May take 10-30 seconds)")
        passed, details = test_execute_streaming()
        print_result("Streaming Execution", passed, details)
        results.append(("Streaming Execution", passed))
        
        # Summary
        print_header("Test Summary")
        passed_count = sum(1 for _, p in results if p)
        total_count = len(results)
        
        for test_name, passed in results:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} - {test_name}")
        
        print(f"\nTotal: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("\n[SUCCESS] All tests passed!")
            return 0
        else:
            print(f"\n[WARNING] {total_count - passed_count} test(s) failed")
            return 1
            
    finally:
        # Clean up server if we started it
        if server_process:
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
            except:
                try:
                    server_process.kill()
                except:
                    pass

if __name__ == "__main__":
    sys.exit(main())

