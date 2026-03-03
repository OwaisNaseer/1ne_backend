#!/usr/bin/env python3
"""
Manual test script for LinkedIn Guide capability API.

Usage:
  # With auth token (get from login or frontend):
  export AUTH_TOKEN="your-jwt-here"
  python scripts/test_linkedin_guide_api.py

  # Or pass base URL and token as args:
  python scripts/test_linkedin_guide_api.py http://localhost:8000 "your-jwt"

  # Without auth (will get 401 if endpoint requires auth):
  python scripts/test_linkedin_guide_api.py http://localhost:8000
"""
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")

if len(sys.argv) >= 2:
    BASE_URL = sys.argv[1].rstrip("/")
if len(sys.argv) >= 3:
    AUTH_TOKEN = sys.argv[2]

URL = f"{BASE_URL}/api/v1/chatbots/career-readiness-coach/capabilities/linkedin_guide"
PAYLOAD = {
    "input": "LinkedIn Guide",
    "parameters": {
        "grade_level": "K-5",
        "region": "United States",
        "industry": "Technology",
        "career_level": "Entry",
    },
    "save_result": False,
}

headers = {"Content-Type": "application/json"}
if AUTH_TOKEN:
    headers["Authorization"] = f"Bearer {AUTH_TOKEN}"


def main():
    print(f"POST {URL}")
    print(f"Payload: {json.dumps(PAYLOAD, indent=2)}")
    print()

    try:
        r = requests.post(URL, json=PAYLOAD, headers=headers, timeout=120)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    print(f"Status: {r.status_code}")
    try:
        body = r.json()
        print(f"Response: {json.dumps(body, indent=2)[:2000]}")
        if len(json.dumps(body)) > 2000:
            print("... (truncated)")
    except Exception:
        print(f"Response (raw): {r.text[:1000]}")

    if r.status_code == 200:
        # Verify result is JSON-serializable (no bytes)
        try:
            json.dumps(body)
            print("\nOK: Response is JSON-serializable.")
        except TypeError as e:
            print(f"\nFAIL: Response is not JSON-serializable: {e}")
            sys.exit(1)
    else:
        print(f"\nFAIL: Expected 200, got {r.status_code}")
        sys.exit(1)


if __name__ == "__main__":
    main()
