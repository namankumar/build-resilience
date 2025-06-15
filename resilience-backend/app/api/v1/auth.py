from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.security import create_access_token, get_current_user
from app.core.database import get_supabase
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserSignUp):
    """Sign up a new user"""
    try:
        supabase = get_supabase()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {"name": user_data.name} if user_data.name else {}
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": auth_response.user.id}, 
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            access_token=access_token,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": user_data.name
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

@router.post("/signin", response_model=AuthResponse)
async def sign_in(user_data: UserSignIn):
    """Sign in an existing user"""
    try:
        supabase = get_supabase()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": auth_response.user.id}, 
            expires_delta=access_token_expires
        )
        
        return AuthResponse(
            access_token=access_token,
            user={
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": auth_response.user.user_metadata.get("name")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/signout")
async def sign_out():
    """Sign out user (client-side token cleanup)"""
    return {"message": "Signed out successfully"}

@router.get("/me")
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current user information"""
    try:
        supabase = get_supabase()
        
        # Get user data from Supabase
        response = supabase.table("users").select("*").eq("id", current_user).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )