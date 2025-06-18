#!/usr/bin/env python3
"""Quick test to get a Supabase token and test backend authentication"""

import requests
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
BASE_URL = "http://10.0.0.93:8001"

# Create client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("🧪 Testing Authentication Fix")
print("=" * 40)

# Try to sign in with an existing user (or create one)
try:
    # Try to sign in with test user
    response = supabase.auth.sign_in_with_password({
        "email": "test@resilience.app", 
        "password": "password123"
    })
    
    if response.session:
        token = response.session.access_token
        print(f"✅ Got Supabase token: {token[:50]}...")
        
        # Test backend API
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test current streak endpoint
        api_response = requests.get(f"{BASE_URL}/api/v1/streaks/current", headers=headers)
        
        if api_response.status_code == 200:
            print("✅ Backend authentication WORKING!")
            print(f"   Response: {api_response.json()}")
        else:
            print(f"❌ Backend auth failed: {api_response.status_code}")
            print(f"   Error: {api_response.text}")
    else:
        print("❌ No session from Supabase")
        
except Exception as e:
    print(f"❌ Auth test failed: {str(e)}")
    
    # Try creating a new user
    try:
        print("\n🔄 Trying to create test user...")
        signup_response = supabase.auth.sign_up({
            "email": "test@resilience.app",
            "password": "password123",
            "options": {"data": {"name": "Test User"}}
        })
        print(f"✅ User created or already exists")
    except Exception as signup_error:
        print(f"❌ Signup failed: {str(signup_error)}")