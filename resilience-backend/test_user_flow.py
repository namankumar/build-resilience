#!/usr/bin/env python3
"""
Complete user flow test for the Resilience App
Tests: Sign up -> Create reflection -> Generate reframe -> Get wins -> Complete win -> Check streak
"""

import requests
import json
import time
import uuid
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://10.0.0.93:8001"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("EXPO_PUBLIC_SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ6aW5nemtkc3Znc2lmY2Ztc3ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwNDg5NTMsImV4cCI6MjA2NTYyNDk1M30._nD9ZzgHnfhKNoQmfbo7i5tSxzEarG16H3Qw2D9BW9Q")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def log_step(step_name, details=""):
    print(f"\n🔍 {step_name}")
    if details:
        print(f"   {details}")

def log_success(message):
    print(f"✅ {message}")

def log_error(message):
    print(f"❌ {message}")

def create_test_user():
    """Create a test user via Supabase auth"""
    log_step("Creating test user")
    
    test_email = f"test{uuid.uuid4().hex[:8]}@gmail.com"
    test_password = "password123"
    
    try:
        response = supabase.auth.sign_up({
            "email": test_email,
            "password": test_password,
            "options": {
                "data": {"name": "Test User"}
            }
        })
        
        if response.user:
            log_success(f"User created: {test_email}")
            
            # For new signups, we need to sign in to get a session
            sign_in_response = supabase.auth.sign_in_with_password({
                "email": test_email,
                "password": test_password
            })
            
            if sign_in_response.session:
                return sign_in_response.session.access_token, test_email
            else:
                log_error("Failed to get session after signup")
                return None, None
        else:
            log_error("Failed to create user")
            return None, None
            
    except Exception as e:
        log_error(f"Error creating user: {str(e)}")
        return None, None

def test_api_with_auth(token):
    """Test API endpoints with authentication"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Create reflection
    log_step("Creating reflection")
    reflection_data = {
        "content": "I'm feeling overwhelmed with work and life balance. Had a stressful day and ate more than I planned.",
        "mood_emoji": "😰",
        "mood_intensity": 6
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/reflections/",
            json=reflection_data,
            headers=headers
        )
        
        if response.status_code == 200:
            reflection = response.json()
            log_success(f"Reflection created: {reflection['id']}")
            
            # Test 2: Generate reframe
            log_step("Generating reframe")
            reframe_response = requests.post(
                f"{BASE_URL}/api/v1/reframes/generate",
                json={"reflection_id": reflection["id"]},
                headers=headers
            )
            
            if reframe_response.status_code == 200:
                reframe = reframe_response.json()
                log_success(f"Reframe generated: {len(reframe['content'])} characters")
                print(f"   Reframe content: {reframe['content'][:100]}...")
                
                # Test 3: Get suggested wins
                log_step("Getting suggested wins")
                wins_response = requests.get(
                    f"{BASE_URL}/api/v1/wins/suggest?reflection_id={reflection['id']}&mood=6",
                    headers=headers
                )
                
                if wins_response.status_code == 200:
                    wins = wins_response.json()
                    log_success(f"Got {len(wins)} suggested wins")
                    
                    if wins:
                        # Test 4: Complete a win
                        log_step("Completing first win")
                        first_win = wins[0]
                        print(f"   Completing: {first_win['title']}")
                        
                        complete_response = requests.post(
                            f"{BASE_URL}/api/v1/wins/complete",
                            json={
                                "win_id": first_win["id"],
                                "reflection_id": reflection["id"],
                                "mood_after": 7,
                                "notes": "This helped me feel a bit better"
                            },
                            headers=headers
                        )
                        
                        if complete_response.status_code == 200:
                            log_success("Win completed successfully")
                            
                            # Test 5: Check streak
                            log_step("Checking streak")
                            streak_response = requests.get(
                                f"{BASE_URL}/api/v1/streaks/current",
                                headers=headers
                            )
                            
                            if streak_response.status_code == 200:
                                streak = streak_response.json()
                                log_success(f"Current streak: {streak['current_streak']} days")
                                return True
                            else:
                                log_error(f"Failed to get streak: {streak_response.status_code}")
                        else:
                            log_error(f"Failed to complete win: {complete_response.status_code}")
                    else:
                        log_error("No wins returned")
                else:
                    log_error(f"Failed to get wins: {wins_response.status_code}")
            else:
                log_error(f"Failed to generate reframe: {reframe_response.status_code}")
                print(f"Response: {reframe_response.text}")
        else:
            log_error(f"Failed to create reflection: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        log_error(f"API test error: {str(e)}")
    
    return False

def main():
    print("🚀 Testing Complete User Flow for Resilience App")
    print("=" * 50)
    
    # Test backend health
    log_step("Testing backend health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            log_success("Backend is healthy")
        else:
            log_error(f"Backend unhealthy: {response.status_code}")
            return
    except Exception as e:
        log_error(f"Cannot reach backend: {str(e)}")
        return
    
    # Create test user and get token
    token, email = create_test_user()
    if not token:
        log_error("Cannot proceed without valid user")
        return
    
    # Wait a moment for user creation to propagate
    time.sleep(2)
    
    # Test complete API flow
    success = test_api_with_auth(token)
    
    if success:
        print("\n" + "=" * 50)
        log_success("🎉 COMPLETE USER FLOW TEST PASSED!")
        print(f"   Test user: {email}")
        print(f"   Full journey: Sign up → Reflection → Reframe → Wins → Streak")
    else:
        print("\n" + "=" * 50)
        log_error("❌ USER FLOW TEST FAILED")
        print("   Check the logs above for specific issues")

if __name__ == "__main__":
    main()