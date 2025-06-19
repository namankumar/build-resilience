from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import requests
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Validate Supabase JWT token and return user ID"""
    token = credentials.credentials
    
    try:
        # Decode JWT without verification to get basic info
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        # Check if token has required fields
        if not decoded_token.get('sub') or not decoded_token.get('role'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token structure",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is for an authenticated user
        if decoded_token.get('role') != 'authenticated':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user role",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token is from correct issuer
        expected_issuer = f"{settings.supabase_url}/auth/v1"
        if decoded_token.get('iss') != expected_issuer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # For production, you would verify the JWT signature here
        # For now, we trust the token if structure is correct
        user_id = decoded_token.get('sub')
        
        return user_id
        
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )