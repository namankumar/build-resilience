from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from app.models.reflection import ReflectionCreate, ReflectionResponse, ReflectionUpdate
from app.core.security import get_current_user
from app.core.database import get_supabase

router = APIRouter(prefix="/reflections", tags=["reflections"])

@router.post("/", response_model=ReflectionResponse, status_code=status.HTTP_201_CREATED)
async def create_reflection(
    reflection: ReflectionCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a new reflection"""
    try:
        supabase = get_supabase()
        
        reflection_data = {
            "id": str(uuid4()),
            "user_id": current_user,
            "content": reflection.content,
            "mood_emoji": reflection.mood_emoji,
            "mood_intensity": reflection.mood_intensity,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("reflections").insert(reflection_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create reflection"
            )
        
        return ReflectionResponse(**response.data[0])
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/", response_model=List[ReflectionResponse])
async def get_user_reflections(
    current_user: str = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's reflections with pagination"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("reflections").select("*").eq(
            "user_id", current_user
        ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        return [ReflectionResponse(**item) for item in response.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/{reflection_id}", response_model=ReflectionResponse)
async def get_reflection(
    reflection_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Get a specific reflection"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("reflections").select("*").eq(
            "id", str(reflection_id)
        ).eq("user_id", current_user).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        return ReflectionResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.put("/{reflection_id}", response_model=ReflectionResponse)
async def update_reflection(
    reflection_id: UUID,
    reflection_update: ReflectionUpdate,
    current_user: str = Depends(get_current_user)
):
    """Update a reflection"""
    try:
        supabase = get_supabase()
        
        # Check if reflection exists and belongs to user
        existing = supabase.table("reflections").select("*").eq(
            "id", str(reflection_id)
        ).eq("user_id", current_user).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        # Update only provided fields
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        if reflection_update.content is not None:
            update_data["content"] = reflection_update.content
        if reflection_update.mood_emoji is not None:
            update_data["mood_emoji"] = reflection_update.mood_emoji
        if reflection_update.mood_intensity is not None:
            update_data["mood_intensity"] = reflection_update.mood_intensity
        
        response = supabase.table("reflections").update(update_data).eq(
            "id", str(reflection_id)
        ).execute()
        
        return ReflectionResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete("/{reflection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reflection(
    reflection_id: UUID,
    current_user: str = Depends(get_current_user)
):
    """Delete a reflection"""
    try:
        supabase = get_supabase()
        
        # Check if reflection exists and belongs to user
        existing = supabase.table("reflections").select("id").eq(
            "id", str(reflection_id)
        ).eq("user_id", current_user).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        supabase.table("reflections").delete().eq(
            "id", str(reflection_id)
        ).execute()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )