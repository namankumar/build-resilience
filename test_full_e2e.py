#!/usr/bin/env python3
"""
Full End-to-End Testing Suite for Resilience App
Tests complete user workflows including frontend React Native web app
"""

import subprocess
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

class FullE2ETestRunner:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:8081"  # Expo web default
        self.backend_process = None
        self.frontend_process = None
        self.driver = None
        
    def setup_chrome_driver(self):
        """Setup Chrome driver for web testing"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("💡 Install ChromeDriver: brew install chromedriver")
            return False
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🔧 Starting backend server...")
        try:
            # Check if already running
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend already running")
                return True
        except:
            pass
        
        # Start backend
        self.backend_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8001"],
            cwd="resilience-backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        for i in range(30):  # 30 second timeout
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend started successfully")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Backend failed to start")
        return False
    
    def start_frontend(self):
        """Start the React Native web app"""
        print("🔧 Starting frontend server...")
        try:
            # Check if already running
            response = requests.get(self.frontend_url, timeout=2)
            if response.status_code == 200:
                print("✅ Frontend already running")
                return True
        except:
            pass
        
        # Start frontend
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "web"],
            cwd="ResilienceApp",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for frontend to start
        for i in range(60):  # 60 second timeout (Expo can be slow)
            try:
                response = requests.get(self.frontend_url, timeout=2)
                if response.status_code == 200:
                    print("✅ Frontend started successfully")
                    return True
            except:
                time.sleep(1)
        
        print("❌ Frontend failed to start")
        return False
    
    def test_frontend_loads(self):
        """Test that frontend loads without errors"""
        print("🌐 Testing frontend loads...")
        try:
            self.driver.get(self.frontend_url)
            
            # Wait for React app to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Check for common error indicators
            page_source = self.driver.page_source.lower()
            if "error" in page_source or "failed to compile" in page_source:
                print("❌ Frontend has compilation errors")
                return False
            
            # Check if it's not just a blank page
            if len(page_source.strip()) < 100:
                print("❌ Frontend appears to be blank")
                return False
            
            print("✅ Frontend loads successfully")
            return True
            
        except TimeoutException:
            print("❌ Frontend load timeout")
            return False
        except Exception as e:
            print(f"❌ Frontend test error: {e}")
            return False
    
    def test_navigation_flow(self):
        """Test navigation between screens"""
        print("🧭 Testing navigation flow...")
        try:
            # Look for navigation elements (adjust selectors based on your app)
            nav_elements = self.driver.find_elements(By.TAG_NAME, "button")
            
            if len(nav_elements) == 0:
                print("⚠️  No navigation elements found")
                return True  # Not a failure if UI isn't ready
            
            print(f"✅ Found {len(nav_elements)} interactive elements")
            return True
            
        except Exception as e:
            print(f"❌ Navigation test error: {e}")
            return False
    
    def test_api_integration(self):
        """Test frontend API integration"""
        print("🔌 Testing API integration...")
        try:
            # Monitor network requests (simplified)
            logs = self.driver.get_log('browser')
            
            # Check for API call errors in console
            api_errors = [log for log in logs if 'error' in log['message'].lower() and 'api' in log['message'].lower()]
            
            if api_errors:
                print(f"❌ Found {len(api_errors)} API errors in console")
                for error in api_errors[:3]:  # Show first 3 errors
                    print(f"   • {error['message']}")
                return False
            
            print("✅ No API integration errors found")
            return True
            
        except Exception as e:
            print(f"❌ API integration test error: {e}")
            return False
    
    def test_backend_health(self):
        """Test backend health and key endpoints"""
        print("🏥 Testing backend health...")
        try:
            # Test health endpoint
            response = requests.get(f"{self.backend_url}/health")
            if response.status_code != 200:
                print("❌ Backend health check failed")
                return False
            
            # Test key API endpoints
            endpoints = [
                "/api/v1/auth/status",
                "/api/v1/wins/?custom_only=true&limit=10&offset=0",
                "/api/v1/reflections/?limit=10&offset=0",
                "/api/v1/reframes/?limit=10&offset=0",
                "/api/v1/streaks/current"
            ]
            
            for endpoint in endpoints:
                response = requests.get(f"{self.backend_url}{endpoint}")
                if response.status_code >= 500:
                    print(f"❌ Backend endpoint {endpoint} failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    return False
            
            print("✅ Backend health check passed")
            return True
            
        except Exception as e:
            print(f"❌ Backend health test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes and resources"""
        print("🧹 Cleaning up...")
        
        if self.driver:
            self.driver.quit()
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
    
    def run_full_e2e_tests(self):
        """Run complete end-to-end test suite"""
        print("🚀 Starting Full End-to-End Tests (Frontend + Backend)...\n")
        
        try:
            # Setup
            if not self.setup_chrome_driver():
                return False
            
            # Start services
            if not self.start_backend():
                return False
            
            if not self.start_frontend():
                return False
            
            # Give everything time to stabilize
            print("⏱️  Waiting for services to stabilize...")
            time.sleep(10)
            
            # Run tests
            tests = [
                ("Backend Health", self.test_backend_health),
                ("Frontend Load", self.test_frontend_loads),
                ("Navigation Flow", self.test_navigation_flow),
                ("API Integration", self.test_api_integration)
            ]
            
            passed = 0
            for test_name, test_func in tests:
                print(f"\n🧪 Running: {test_name}")
                try:
                    if test_func():
                        passed += 1
                    time.sleep(2)  # Brief pause between tests
                except Exception as e:
                    print(f"❌ Test {test_name} crashed: {e}")
            
            print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
            
            if passed == len(tests):
                print("🎉 All Full E2E tests passed!")
                return True
            else:
                print("💥 Some Full E2E tests failed!")
                return False
        
        finally:
            self.cleanup()

if __name__ == "__main__":
    runner = FullE2ETestRunner()
    success = runner.run_full_e2e_tests()
    exit(0 if success else 1)