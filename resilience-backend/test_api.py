#!/usr/bin/env python3
"""
API Test Suite for Resilience App Backend
Tests all major API endpoints with mock data
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8001"
TIMEOUT = 5

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def test_endpoint(self, method, endpoint, data=None, expected_status=200, description=""):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n🧪 Testing {method} {endpoint}")
        if description:
            print(f"   Description: {description}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=TIMEOUT)
            else:
                print(f"   ❌ Unsupported method: {method}")
                return False
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == expected_status:
                print(f"   ✅ SUCCESS")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
                self.test_results.append({"endpoint": endpoint, "status": "PASS"})
                return True
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                self.test_results.append({"endpoint": endpoint, "status": "FAIL"})
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAILED - Connection error: {e}")
            self.test_results.append({"endpoint": endpoint, "status": "ERROR"})
            return False

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting Resilience App API Test Suite")
        print(f"   Base URL: {self.base_url}")
        print(f"   Time: {datetime.now().isoformat()}")
        print("="*60)

        # 1. Health checks
        self.test_endpoint("GET", "/", description="Root endpoint health check")
        self.test_endpoint("GET", "/health", description="Health check endpoint")

        # 2. Reflections API
        print("\n📝 TESTING REFLECTIONS API")
        
        # Create reflection
        reflection_data = {
            "content": "I'm feeling overwhelmed today and struggled with emotional eating",
            "mood_emoji": "😰",
            "mood_intensity": 7
        }
        self.test_endpoint("POST", "/api/v1/reflections/", 
                          data=reflection_data,
                          expected_status=200,
                          description="Create new reflection")
        
        # Get reflections
        self.test_endpoint("GET", "/api/v1/reflections/",
                          description="Get user reflections list")

        # 3. Reframes API
        print("\n🔄 TESTING REFRAMES API")
        
        reframe_request = {
            "reflection_id": "test-reflection-id",
            "user_context": {"mood_intensity": 7}
        }
        self.test_endpoint("POST", "/api/v1/reframes/generate",
                          data=reframe_request,
                          description="Generate AI reframe")

        # 4. Wins API
        print("\n✨ TESTING WINS API")
        
        self.test_endpoint("GET", "/api/v1/wins/suggest?reflection_id=test-id&mood=7",
                          description="Get suggested wins")

        # 5. Streaks API
        print("\n📈 TESTING STREAKS API")
        
        self.test_endpoint("GET", "/api/v1/streaks/current",
                          description="Get current streak")

        # 6. Error handling
        print("\n❌ TESTING ERROR HANDLING")
        
        self.test_endpoint("GET", "/api/v1/nonexistent",
                          expected_status=404,
                          description="Non-existent endpoint")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        error_tests = len([t for t in self.test_results if t["status"] == "ERROR"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Errors: {error_tests}")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n🔍 FAILED/ERROR TESTS:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"   {result['status']}: {result['endpoint']}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 API is in good shape!")
        elif success_rate >= 60:
            print("⚠️  API needs some fixes")
        else:
            print("🚨 API has major issues")

def wait_for_server(base_url, max_attempts=10):
    """Wait for server to be ready"""
    print(f"⏳ Waiting for server at {base_url} to be ready...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_attempts} - Server not ready yet...")
        time.sleep(2)
    
    print(f"❌ Server not ready after {max_attempts} attempts")
    return False

if __name__ == "__main__":
    # Check if server is running
    if not wait_for_server(BASE_URL):
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python -m uvicorn test_server:app --host 127.0.0.1 --port 8001")
        sys.exit(1)
    
    # Run tests
    tester = APITester(BASE_URL)
    tester.run_all_tests()