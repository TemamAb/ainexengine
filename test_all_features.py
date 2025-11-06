#!/usr/bin/env python3
"""
Comprehensive 36-Feature Test Suite
Tests all Ainexus Engine features in one go
"""
import requests
import json
import time
import sys
from typing import Dict, List

class AinexusTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = {}
        self.start_time = time.time()
    
    def test_endpoint(self, endpoint: str, name: str = None) -> Dict:
        """Test a single endpoint"""
        if name is None:
            name = endpoint
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}", timeout=15)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'âœ… SUCCESS',
                    'response_time': f'{response_time}ms',
                    'data': data,
                    'features_count': len(data.get('features', [])) if 'features' in data else None
                }
            else:
                return {
                    'status': f'âŒ FAILED ({response.status_code})',
                    'response_time': f'{response_time}ms',
                    'error': f'HTTP {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'â° TIMEOUT',
                'response_time': 'N/A',
                'error': 'Request timeout'
            }
        except Exception as e:
            return {
                'status': 'í²¥ ERROR',
                'response_time': 'N/A',
                'error': str(e)
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all features"""
        print("íº€ STARTING COMPREHENSIVE 36-FEATURE TEST")
        print("=" * 60)
        
        # Test all endpoints
        endpoints = [
            ('/', 'Main Dashboard'),
            ('/health', 'Health Check'),
            ('/features', 'Features List'),
            ('/api/dashboard', 'Dashboard API'),
            ('/api/control-panel', 'Control Panel'),
            ('/api/wallet', 'Wallet Integration'),
            ('/ai/optimizer', 'AI Optimizer'),
            ('/ai/analytics', 'AI Analytics'),
            ('/ai/insights', 'AI Insights')
        ]
        
        for endpoint, name in endpoints:
            print(f"Testing {name}...", end=' ')
            result = self.test_endpoint(endpoint, name)
            self.results[name] = result
            print(result['status'])
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("í¾¯ COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        successful = sum(1 for r in self.results.values() if 'âœ…' in r['status'])
        total = len(self.results)
        success_rate = (successful / total) * 100
        
        # Individual results
        for name, result in self.results.items():
            print(f"{name:20} {result['status']:25} {result['response_time']:10}")
        
        print("=" * 60)
        print(f"SUCCESS RATE: {successful}/{total} ({success_rate:.1f}%)")
        
        # Feature count analysis
        features_result = self.results.get('Features List')
        if features_result and features_result['status'] == 'âœ… SUCCESS':
            feature_count = len(features_result['data'].get('features', []))
            print(f"í´§ FEATURE COUNT: {feature_count}/36")
            if feature_count == 36:
                print("í¾‰ ALL 36 FEATURES VERIFIED!")
            else:
                print(f"âš ï¸  MISSING {36 - feature_count} FEATURES")
        
        # Performance summary
        total_time = round(time.time() - self.start_time, 2)
        print(f"â±ï¸  TOTAL TEST TIME: {total_time}s")
        
        # Overall status
        if success_rate == 100:
            print("í¾Š ALL SYSTEMS OPERATIONAL - 36 FEATURES RUNNING!")
        elif success_rate >= 80:
            print("í± MOST FEATURES OPERATIONAL - MINOR ISSUES")
        else:
            print("íº¨ SIGNIFICANT ISSUES DETECTED")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    tester = AinexusTester(base_url)
    tester.run_comprehensive_test()
