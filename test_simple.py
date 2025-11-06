#!/usr/bin/env python3
import requests
import time
import sys

def test_endpoint(base_url, endpoint):
    try:
        start = time.time()
        response = requests.get(f"{base_url}{endpoint}", timeout=10)
        response_time = round((time.time() - start) * 1000, 2)
        
        if response.status_code == 200:
            data = response.json()
            features = len(data.get('features', [])) if 'features' in data else 0
            return True, f"SUCCESS ({response_time}ms, features: {features})", data
        else:
            return False, f"FAILED (HTTP {response.status_code})", None
    except Exception as e:
        return False, f"ERROR: {str(e)}", None

def main():
    base_url = "http://ainexus-engine:5000"
    print("Testing Ainexus Engine...")
    
    endpoints = [
        ("/", "Main Dashboard"),
        ("/health", "Health Check"),
        ("/features", "Features List"),
        ("/ai/optimizer", "AI Optimizer")
    ]
    
    results = []
    all_passed = True
    
    for endpoint, name in endpoints:
        print(f"Testing {name}...", end=" ")
        passed, message, data = test_endpoint(base_url, endpoint)
        results.append((name, passed, message))
        
        if passed:
            print("PASS")
        else:
            print("FAIL")
            all_passed = False
    
    print("\n=== RESULTS ===")
    for name, passed, message in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status} - {message}")
    
    # Check feature count
    features_result = next((r for r in results if r[0] == "Features List"), None)
    if features_result and features_result[1]:
        print(f"\nFeature Count: {features_result[2].get('total_features', 'N/A')}/36")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
