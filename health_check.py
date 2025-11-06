#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get("http://localhost:5000/health", timeout=5)
    if response.status_code == 200:
        print("✅ Engine is healthy")
        sys.exit(0)
    else:
        print(f"❌ Engine unhealthy: HTTP {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Engine unreachable: {e}")
    sys.exit(1)
