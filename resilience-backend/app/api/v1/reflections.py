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
            "user_id": current_user,
            "content": reflection.content,
        }
        
        # Add mood_emoji if provided
        if reflection.mood_emoji is not None:
            reflection_data["mood_emoji"] = reflection.mood_emoji
        
        # Add mood_intensity if provided (now stored directly)
        if reflection.mood_intensity is not None:
            reflection_data["mood_intensity"] = reflection.mood_intensity
            
            # Also map to mood enum for backward compatibility
            if reflection.mood_intensity <= 2:
                reflection_data["mood"] = "very_negative"
            elif reflection.mood_intensity <= 4:
                reflection_data["mood"] = "negative" 
            elif reflection.mood_intensity <= 6:
                reflection_data["mood"] = "neutral"
            elif reflection.mood_intensity <= 8:
                reflection_data["mood"] = "positive"
            else:
                reflection_data["mood"] = "very_positive"
        
        response = supabase.table("reflections").insert(reflection_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create reflection"
            )
        
        # Map database response to model format
        db_reflection = response.data[0]
        model_data = {
            "id": db_reflection["id"],
            "content": db_reflection["content"],
            "mood_emoji": db_reflection.get("mood_emoji"),
            "mood_intensity": db_reflection.get("mood_intensity"),
            "created_at": db_reflection["created_at"]
        }
        
        return ReflectionResponse(**model_data)
        
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
        
        # Map database responses to model format
        reflections = []
        for item in response.data:
            model_data = {
                "id": item["id"],
                "content": item["content"],
                "mood_emoji": item.get("mood_emoji"),
                "mood_intensity": item.get("mood_intensity"),
                "created_at": item["created_at"]
            }
            reflections.append(ReflectionResponse(**model_data))
        
        return reflections
        
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