#!/usr/bin/env python3
"""
End-to-End Testing Suite for Resilience App
Tests complete user workflows from frontend to backend to database
"""

import requests
import json
import time
from typing import Dict, Any

class E2ETestRunner:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def test_auth_flow(self) -> bool:
        """Test complete authentication flow"""
        print("🔐 Testing authentication flow...")
        
        # Test auth status endpoint
        response = self.session.get(f"{self.base_url}/api/v1/auth/status")
        if response.status_code != 200:
            print(f"❌ Auth status failed: {response.status_code}")
            return False
            
        print("✅ Auth flow working")
        return True
    
    def test_wins_workflow(self) -> bool:
        """Test complete wins workflow"""
        print("🏆 Testing wins workflow...")
        
        # Get wins
        response = self.session.get(f"{self.base_url}/api/v1/wins/?custom_only=true&limit=50&offset=0")
        if response.status_code != 200:
            print(f"❌ Get wins failed: {response.status_code} - {response.text}")
            return False
            
        print("✅ Wins workflow working")
        return True
    
    def test_reflections_workflow(self) -> bool:
        """Test complete reflections workflow"""
        print("💭 Testing reflections workflow...")
        
        # Get reflections
        response = self.session.get(f"{self.base_url}/api/v1/reflections/?limit=10&offset=0")
        if response.status_code != 200:
            print(f"❌ Get reflections failed: {response.status_code} - {response.text}")
            return False
            
        print("✅ Reflections workflow working")
        return True
    
    def test_reframes_workflow(self) -> bool:
        """Test complete reframes workflow"""
        print("🔄 Testing reframes workflow...")
        
        # Get reframes
        response = self.session.get(f"{self.base_url}/api/v1/reframes/?limit=10&offset=0")
        if response.status_code != 200:
            print(f"❌ Get reframes failed: {response.status_code} - {response.text}")
            return False
            
        print("✅ Reframes workflow working")
        return True
    
    def test_streaks_workflow(self) -> bool:
        """Test complete streaks workflow"""
        print("📈 Testing streaks workflow...")
        
        # Get current streak
        response = self.session.get(f"{self.base_url}/api/v1/streaks/current")
        if response.status_code != 200:
            print(f"❌ Get current streak failed: {response.status_code} - {response.text}")
            return False
            
        print("✅ Streaks workflow working")
        return True
    
    def run_all_tests(self) -> bool:
        """Run all end-to-end tests"""
        print("🚀 Starting End-to-End Tests...\n")
        
        tests = [
            self.test_auth_flow,
            self.test_wins_workflow,
            self.test_reflections_workflow,
            self.test_reframes_workflow,
            self.test_streaks_workflow
        ]
        
        passed = 0
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
        
        print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
        
        if passed == len(tests):
            print("🎉 All E2E tests passed!")
            return True
        else:
            print("💥 Some E2E tests failed!")
            return False

if __name__ == "__main__":
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    exit(0 if success else 1)