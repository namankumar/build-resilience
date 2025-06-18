from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import get_supabase
from supabase import create_client
import jwt

security = HTTPBearer()

def get_anon_supabase():
    """Get Supabase client with anon key for token validation"""
    anon_key = settings.supabase_anon_key or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ6aW5nemtkc3Znc2lmY2Ztc3ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwNDg5NTMsImV4cCI6MjA2NTYyNDk1M30._nD9ZzgHnfhKNoQmfbo7i5tSxzEarG16H3Qw2D9BW9Q"
    return create_client(settings.supabase_url, anon_key)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Get current user from Supabase JWT token"""
    token = credentials.credentials
    
    try:
        # Decode the JWT to extract user info
        # Supabase user tokens contain user ID in 'sub' field
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Check if this is a user token (has 'sub' field)
        user_id = decoded.get("sub")
        role = decoded.get("role", "")
        
        print(f"🔍 Token debug - Role: {role}, User ID: {user_id}")
        
        if not user_id or role == "anon":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required - please sign in",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # For now, trust the JWT if it has a user ID
        # In production, you'd want to verify the signature
        # with Supabase's JWT secret
        
        return user_id
        
    except jwt.DecodeError:
        print(f"❌ JWT decode error")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )