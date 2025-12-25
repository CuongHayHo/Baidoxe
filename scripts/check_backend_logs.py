#!/usr/bin/env python3
"""
check_backend_logs.py - Kiểm tra logs trong backend
"""

import requests
import json

BACKEND_URL = "http://localhost:5000"

def check_logs():
    try:
        response = requests.get(f"{BACKEND_URL}/api/logs/?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_logs()
