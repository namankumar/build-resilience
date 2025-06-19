#!/usr/bin/env python3
"""
Agentic End-to-End Testing for Resilience App
Uses AI agents to intelligently test user workflows
"""

import subprocess
import time
import requests
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, Browser
import openai

@dataclass
class TestResult:
    test_name: str
    success: bool
    details: str
    screenshot_path: Optional[str] = None

class AgenticTestAgent:
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        
    async def analyze_page(self, page: Page, goal: str) -> Dict[str, Any]:
        """AI-powered page analysis"""
        try:
            # Get page content and structure
            content = await page.content()
            title = await page.title()
            url = page.url
            
            # Get all interactive elements
            buttons = await page.query_selector_all('button, [role="button"], input[type="submit"]')
            inputs = await page.query_selector_all('input, textarea, select')
            links = await page.query_selector_all('a, [role="link"]')
            
            # Extract text content from elements
            button_texts = []
            for btn in buttons:
                text = await btn.inner_text()
                if text.strip():
                    button_texts.append(text.strip())
            
            input_info = []
            for inp in inputs:
                placeholder = await inp.get_attribute('placeholder')
                input_type = await inp.get_attribute('type')
                input_info.append({
                    'type': input_type or 'text',
                    'placeholder': placeholder or ''
                })
            
            analysis = {
                'url': url,
                'title': title,
                'buttons': button_texts,
                'inputs': input_info,
                'has_errors': 'error' in content.lower() or 'failed' in content.lower(),
                'is_loading': 'loading' in content.lower() or 'spinner' in content.lower(),
                'content_length': len(content)
            }
            
            # AI-powered analysis if available
            if self.client:
                analysis['ai_assessment'] = await self.get_ai_assessment(analysis, goal)
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    async def get_ai_assessment(self, page_data: Dict, goal: str) -> str:
        """Get AI assessment of page state"""
        try:
            prompt = f"""
            Analyze this webpage data for a resilience app testing scenario.
            
            Goal: {goal}
            
            Page Data:
            - URL: {page_data.get('url', 'unknown')}
            - Title: {page_data.get('title', 'unknown')}
            - Buttons: {page_data.get('buttons', [])}
            - Inputs: {page_data.get('inputs', [])}
            - Has Errors: {page_data.get('has_errors', False)}
            - Is Loading: {page_data.get('is_loading', False)}
            
            Provide a brief assessment:
            1. Is the page functioning correctly?
            2. Are there any obvious issues?
            3. What should be tested next?
            
            Keep response under 100 words.
            """
            
            response = await self.client.chat.completions.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI analysis failed: {e}"
    
    async def intelligent_interaction(self, page: Page, goal: str) -> bool:
        """AI-guided interaction with the page"""
        try:
            analysis = await self.analyze_page(page, goal)
            
            if analysis.get('has_errors'):
                return False
            
            # Look for relevant buttons based on goal
            if 'reflection' in goal.lower():
                # Look for reflection-related buttons
                for btn_text in analysis.get('buttons', []):
                    if any(word in btn_text.lower() for word in ['reflect', 'journal', 'write', 'create']):
                        button = await page.query_selector(f'button:has-text("{btn_text}")')
                        if button:
                            await button.click()
                            await page.wait_for_timeout(1000)
                            return True
            
            elif 'wins' in goal.lower():
                # Look for wins-related buttons
                for btn_text in analysis.get('buttons', []):
                    if any(word in btn_text.lower() for word in ['win', 'achievement', 'success']):
                        button = await page.query_selector(f'button:has-text("{btn_text}")')
                        if button:
                            await button.click()
                            await page.wait_for_timeout(1000)
                            return True
            
            return True
            
        except Exception as e:
            print(f"Interaction error: {e}")
            return False

class AgenticE2ERunner:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:8081"
        self.backend_process = None
        self.frontend_process = None
        self.agent = AgenticTestAgent()
        
    async def start_services(self) -> bool:
        """Start backend and frontend services"""
        print("🚀 Starting services...")
        
        # Start backend
        if not await self.start_backend():
            return False
        
        # Start frontend
        if not await self.start_frontend():
            return False
        
        return True
    
    async def start_backend(self) -> bool:
        """Start FastAPI backend"""
        try:
            # Check if already running
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend already running")
                return True
        except:
            pass
        
        print("🔧 Starting backend...")
        self.backend_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--reload", "--port", "8001"],
            cwd="resilience-backend",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for startup
        for i in range(30):
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=1)
                if response.status_code == 200:
                    print("✅ Backend started")
                    return True
            except:
                await asyncio.sleep(1)
        
        return False
    
    async def start_frontend(self) -> bool:
        """Start React Native web app"""
        try:
            response = requests.get(self.frontend_url, timeout=2)
            if response.status_code == 200:
                print("✅ Frontend already running")
                return True
        except:
            pass
        
        print("🔧 Starting frontend...")
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "web"],
            cwd="ResilienceApp",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for startup
        for i in range(60):
            try:
                response = requests.get(self.frontend_url, timeout=2)
                if response.status_code == 200:
                    print("✅ Frontend started")
                    return True
            except:
                await asyncio.sleep(1)
        
        return False
    
    async def test_user_journey(self, journey_name: str, steps: List[str]) -> TestResult:
        """Test a complete user journey using AI guidance"""
        print(f"🎭 Testing user journey: {journey_name}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to app
                await page.goto(self.frontend_url)
                await page.wait_for_load_state('networkidle')
                
                success = True
                details = []
                
                for i, step in enumerate(steps):
                    print(f"  Step {i+1}: {step}")
                    
                    # AI analyzes current page state
                    analysis = await self.agent.analyze_page(page, step)
                    
                    if analysis.get('has_errors'):
                        success = False
                        details.append(f"Step {i+1} failed: Page has errors")
                        break
                    
                    # AI decides how to interact
                    interaction_success = await self.agent.intelligent_interaction(page, step)
                    
                    if not interaction_success:
                        success = False
                        details.append(f"Step {i+1} failed: Could not complete interaction")
                        break
                    
                    details.append(f"Step {i+1} completed: {step}")
                    await asyncio.sleep(1)
                
                # Take screenshot for analysis
                screenshot_path = f"test_screenshots/{journey_name.replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_path)
                
                await browser.close()
                
                return TestResult(
                    test_name=journey_name,
                    success=success,
                    details="\n".join(details),
                    screenshot_path=screenshot_path
                )
                
            except Exception as e:
                await browser.close()
                return TestResult(
                    test_name=journey_name,
                    success=False,
                    details=f"Journey failed: {e}"
                )
    
    async def test_api_health(self) -> TestResult:
        """Test backend API health intelligently"""
        print("🏥 Testing API health...")
        
        try:
            endpoints = [
                ("/health", "Health check"),
                ("/api/v1/auth/status", "Auth status"),
                ("/api/v1/wins/?limit=5", "Wins endpoint"),
                ("/api/v1/reflections/?limit=5", "Reflections endpoint"),
                ("/api/v1/reframes/?limit=5", "Reframes endpoint"),
                ("/api/v1/streaks/current", "Current streak")
            ]
            
            results = []
            all_passed = True
            
            for endpoint, description in endpoints:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                    if response.status_code >= 500:
                        all_passed = False
                        results.append(f"❌ {description}: {response.status_code}")
                        if response.text:
                            results.append(f"   Error: {response.text[:100]}")
                    else:
                        results.append(f"✅ {description}: {response.status_code}")
                except Exception as e:
                    all_passed = False
                    results.append(f"❌ {description}: {e}")
            
            return TestResult(
                test_name="API Health Check",
                success=all_passed,
                details="\n".join(results)
            )
            
        except Exception as e:
            return TestResult(
                test_name="API Health Check",
                success=False,
                details=f"Health check failed: {e}"
            )
    
    async def run_agentic_tests(self) -> bool:
        """Run all agentic E2E tests"""
        print("🤖 Starting Agentic End-to-End Tests...\n")
        
        try:
            # Start services
            if not await self.start_services():
                print("❌ Failed to start services")
                return False
            
            # Wait for stabilization
            print("⏱️  Waiting for services to stabilize...")
            await asyncio.sleep(10)
            
            # Define user journeys to test
            journeys = [
                ("App Loading", ["Load the app homepage", "Check for navigation elements"]),
                ("Reflection Journey", ["Navigate to reflections", "Create a new reflection"]),
                ("Wins Journey", ["Navigate to wins", "View existing wins"]),
                ("Reframe Journey", ["Navigate to reframes", "Access reframe functionality"])
            ]
            
            # Run tests
            results = []
            
            # Test API health first
            api_result = await self.test_api_health()
            results.append(api_result)
            
            # Test user journeys
            for journey_name, steps in journeys:
                result = await self.test_user_journey(journey_name, steps)
                results.append(result)
            
            # Report results
            passed = sum(1 for r in results if r.success)
            total = len(results)
            
            print(f"\n📊 Agentic E2E Results: {passed}/{total} tests passed")
            
            for result in results:
                status = "✅" if result.success else "❌"
                print(f"{status} {result.test_name}")
                if not result.success:
                    print(f"   {result.details}")
            
            if passed == total:
                print("🎉 All agentic E2E tests passed!")
                return True
            else:
                print("💥 Some agentic E2E tests failed!")
                return False
        
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up processes"""
        if self.frontend_process:
            self.frontend_process.terminate()
        if self.backend_process:
            self.backend_process.terminate()

async def main():
    runner = AgenticE2ERunner()
    success = await runner.run_agentic_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))