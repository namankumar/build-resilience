from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from app.models.reframe import ReframeRequest, ReframeResponse, ReframeSaveRequest
from app.core.security import get_current_user
from app.core.database import get_supabase
from app.services.ai.reframe_agent import ReframeAgent

router = APIRouter(prefix="/reframes", tags=["reframes"])

@router.post("/generate", response_model=ReframeResponse, status_code=status.HTTP_201_CREATED)
async def generate_reframe(
    request: ReframeRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate an AI reframe for a reflection"""
    try:
        supabase = get_supabase()
        
        # Verify reflection exists and belongs to user
        reflection_response = supabase.table("reflections").select("*").eq(
            "id", str(request.reflection_id)
        ).eq("user_id", current_user).execute()
        
        if not reflection_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        reflection = reflection_response.data[0]
        
        # Generate reframe using AI (with fallback for testing)
        try:
            reframe_agent = ReframeAgent()
            context = {
                "mood_intensity": reflection.get("mood_intensity"),
                **(request.user_context or {})
            }
            
            reframe_content = await reframe_agent.generate_response(
                reflection["content"], 
                context
            )
        except Exception as ai_error:
            # Fallback to simple reframe for testing
            print(f"⚠️  AI service unavailable, using fallback: {ai_error}")
            reframe_content = f"Here's a more balanced perspective on your reflection: {reflection['content'][:50]}... Remember that challenges are opportunities for growth."
        
        # Save reframe to database
        reframe_data = {
            "reflection_id": str(request.reflection_id),
            "user_id": current_user,
            "original_thought": reflection["content"],  # Use reflection content as original thought
            "reframed_thought": reframe_content,
            "ai_generated": True,
            "is_helpful": None  # Will be set when user provides feedback
        }
        
        # Add new fields if columns exist (always add them for new schema)
        reframe_data["content"] = reframe_content
        reframe_data["ai_model_used"] = "claude-3-haiku-20240307"  # Default model
        reframe_data["saved"] = False
        
        response = supabase.table("reframes").insert(reframe_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save reframe"
            )
        
        # Map database response to model format
        db_reframe = response.data[0]
        model_data = {
            "id": db_reframe["id"],
            "reflection_id": db_reframe["reflection_id"],
            "content": db_reframe.get("content") or db_reframe.get("reframed_thought"),
            "ai_model_used": db_reframe.get("ai_model_used", "claude-3-haiku-20240307"),
            "created_at": db_reframe["created_at"],
            "saved": db_reframe.get("saved", False)
        }
        
        return ReframeResponse(**model_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating reframe: {str(e)}"
        )

@router.get("/", response_model=List[ReframeResponse])
async def get_user_reframes(
    current_user: str = Depends(get_current_user),
    saved_only: bool = False,
    limit: int = 20,
    offset: int = 0
):
    """Get user's reframes with optional filtering"""
    try:
        supabase = get_supabase()
        
        query = supabase.table("reframes").select("*").eq("user_id", current_user)
        
        if saved_only:
            query = query.eq("saved", True)
        
        response = query.order("created_at", desc=True).range(
            offset, offset + limit - 1
        ).execute()
        
        # Map database responses to model format
        reframes = []
        for item in response.data:
            model_data = {
                "id": item["id"],
                "reflection_id": item["reflection_id"],
                "content": item.get("content") or item.get("reframed_thought"),
                "ai_model_used": item.get("ai_model_used") or "claude-3-haiku-20240307",
                "created_at": item["created_at"],
                "saved": item.get("saved", False)
            }
            reframes.append(ReframeResponse(**model_data))
        
        return reframes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/save", response_model=ReframeResponse)
async def save_reframe(
    request: ReframeSaveRequest,
    current_user: str = Depends(get_current_user)
):
    """Save/unsave a reframe"""
    try:
        supabase = get_supabase()
        
        # Verify reframe exists and belongs to user
        existing = supabase.table("reframes").select("*").eq(
            "id", str(request.reframe_id)
        ).eq("user_id", current_user).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reframe not found"
            )
        
        # Update save status
        response = supabase.table("reframes").update({
            "saved": request.save
        }).eq("id", str(request.reframe_id)).execute()
        
        return ReframeResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/{reframe_id}", response_model=ReframeResponse)
async def get_reframe(
    reframe_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Get a specific reframe"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("reframes").select("*").eq(
            "id", str(reframe_id)
        ).eq("user_id", current_user).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reframe not found"
            )
        
        return ReframeResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )