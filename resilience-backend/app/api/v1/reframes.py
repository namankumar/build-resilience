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
        
        # Generate reframe using AI
        reframe_agent = ReframeAgent()
        context = {
            "mood_intensity": reflection.get("mood_intensity"),
            **(request.user_context or {})
        }
        
        reframe_content = await reframe_agent.generate_response(
            reflection["content"], 
            context
        )
        
        # Save reframe to database
        reframe_data = {
            "id": str(uuid4()),
            "reflection_id": str(request.reflection_id),
            "user_id": current_user,
            "content": reframe_content,
            "ai_model_used": reframe_agent.model.value,
            "created_at": datetime.utcnow().isoformat(),
            "saved": False
        }
        
        response = supabase.table("reframes").insert(reframe_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save reframe"
            )
        
        return ReframeResponse(**response.data[0])
        
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
        
        return [ReframeResponse(**item) for item in response.data]
        
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