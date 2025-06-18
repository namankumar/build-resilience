#!/usr/bin/env python3
"""Debug token to understand the structure"""

import jwt
import json

# This is a sample Supabase token structure for reference
sample_anon_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ6aW5nemtkc3Znc2lmY2Ztc3ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwNDg5NTMsImV4cCI6MjA2NTYyNDk1M30._nD9ZzgHnfhKNoQmfbo7i5tSxzEarG16H3Qw2D9BW9Q"

print("🔍 Analyzing Supabase Token Structure")
print("=" * 50)

try:
    # Decode without verification to see structure
    decoded = jwt.decode(sample_anon_token, options={"verify_signature": False})
    print("📋 Token payload:")
    print(json.dumps(decoded, indent=2))
    
    print(f"\n🔑 Token type: {decoded.get('role', 'unknown')}")
    print(f"👤 User ID: {decoded.get('sub', 'none')}")
    print(f"🏢 Issuer: {decoded.get('iss', 'unknown')}")
    
except Exception as e:
    print(f"❌ Error decoding token: {e}")

print(f"\n💡 This is an ANON token, not a user token")
print(f"   User tokens will have 'sub' field with actual user ID")
print(f"   Anon tokens are for anonymous access")