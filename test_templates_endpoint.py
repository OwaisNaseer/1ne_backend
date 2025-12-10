"""Quick test script to verify templates endpoint works."""
import requests
import json

def test_templates_endpoint():
    url = "http://127.0.0.1:8000/api/v1/templates"
    headers = {
        "Accept": "application/json",
        "X-Session-Id": "test-session-123"
    }
    
    print(f"Testing: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Got {len(data)} templates")
            if data:
                print(f"\nFirst template:")
                print(json.dumps(data[0], indent=2, default=str))
        else:
            print(f"\n❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Backend server is not running!")
        print("   Start it with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_templates_endpoint()

