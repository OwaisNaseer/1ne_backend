"""
Quick test script for template endpoints (non-streaming and streaming).
Run this after starting the server with: uvicorn app.main:app --reload
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200

def test_list_templates():
    """Test list templates endpoint."""
    print("Testing list templates endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/templates")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        templates = response.json()
        print(f"Found {len(templates)} templates")
        if templates:
            print(f"First template: {templates[0].get('slug', 'N/A')}\n")
    else:
        print(f"Error: {response.text}\n")
    return response.status_code == 200

def test_execute_template(slug="lesson_planner"):
    """Test non-streaming template execution."""
    print(f"Testing non-streaming execution for '{slug}'...")
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
            timeout=60
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Execution ID: {data.get('execution_id', 'N/A')}")
            print(f"Model Used: {data.get('model_used', 'N/A')}")
            print(f"Provider: {data.get('provider_used', 'N/A')}")
            print(f"Has Output: {bool(data.get('output'))}\n")
            return True
        else:
            print(f"Error: {response.text}\n")
            return False
    except Exception as e:
        print(f"Exception: {e}\n")
        return False

def test_streaming_template(slug="lesson_planner"):
    """Test streaming template execution."""
    print(f"Testing streaming execution for '{slug}'...")
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
            timeout=120
        )
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            print("Streaming events:")
            event_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        event_data = json.loads(line_str[6:])
                        event_type = event_data.get('type', 'unknown')
                        event_count += 1
                        if event_type == 'meta':
                            print(f"  [{event_count}] META: {event_data.get('template_slug')}")
                        elif event_type == 'content':
                            chunk = event_data.get('chunk', '')[:50]
                            print(f"  [{event_count}] CONTENT: {chunk}...")
                        elif event_type == 'done':
                            print(f"  [{event_count}] DONE: Execution ID = {event_data.get('execution_id')}")
                            break
                        elif event_type == 'error':
                            print(f"  [{event_count}] ERROR: {event_data.get('message')}")
                            return False
            
            print(f"Received {event_count} events\n")
            return True
        else:
            print(f"Error: {response.text}\n")
            return False
    except Exception as e:
        print(f"Exception: {e}\n")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing 1ne.ai Backend Endpoints")
    print("=" * 60)
    print()
    
    # Wait a bit for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test list templates
    results.append(("List Templates", test_list_templates()))
    
    # Test non-streaming execution
    results.append(("Non-Streaming Execution", test_execute_template()))
    
    # Test streaming execution
    results.append(("Streaming Execution", test_streaming_template()))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    print()
    if all_passed:
        print("All tests passed! ✓")
    else:
        print("Some tests failed. Check the output above.")

