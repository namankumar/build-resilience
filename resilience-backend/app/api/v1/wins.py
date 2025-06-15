from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from app.models.win import (
    WinCreate, WinResponse, WinCompletionCreate, WinCompletionResponse, 
    WinSuggestionRequest
)
from app.core.security import get_current_user
from app.core.database import get_supabase
from app.services.ai.win_generator import WinGeneratorAgent

router = APIRouter(prefix="/wins", tags=["wins"])

@router.post("/", response_model=WinResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_win(
    win: WinCreate,
    current_user: str = Depends(get_current_user)
):
    """Create a custom win"""
    try:
        supabase = get_supabase()
        
        win_data = {
            "id": str(uuid4()),
            "user_id": current_user,
            "title": win.title,
            "description": win.description,
            "category": win.category.value,
            "estimated_minutes": win.estimated_minutes,
            "is_custom": True,
            "usage_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("wins").insert(win_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create win"
            )
        
        return WinResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/suggest", response_model=List[WinResponse])
async def get_suggested_wins(
    request: WinSuggestionRequest,
    current_user: str = Depends(get_current_user)
):
    """Get AI-suggested wins based on reflection"""
    try:
        supabase = get_supabase()
        
        # Get reflection data
        reflection_response = supabase.table("reflections").select("*").eq(
            "id", str(request.reflection_id)
        ).eq("user_id", current_user).execute()
        
        if not reflection_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        reflection = reflection_response.data[0]
        
        # Get user's successful wins for context
        past_wins = []
        if request.exclude_recent:
            completions_response = supabase.table("win_completions").select(
                "wins(title, category)"
            ).eq("user_id", current_user).order(
                "completed_at", desc=True
            ).limit(10).execute()
            
            past_wins = [
                f"{comp['wins']['title']} ({comp['wins']['category']})" 
                for comp in completions_response.data if comp.get('wins')
            ]
        
        # Generate AI suggestions
        win_generator = WinGeneratorAgent()
        suggested_wins = await win_generator.generate_wins(
            reflection["content"],
            mood_intensity=request.mood_intensity or reflection.get("mood_intensity"),
            user_context={"past_successful_wins": past_wins}
        )
        
        # Convert to WinResponse format and save as system wins
        win_responses = []
        for suggested_win in suggested_wins:
            win_data = {
                "id": str(uuid4()),
                "user_id": current_user,
                "title": suggested_win["title"],
                "description": suggested_win["description"],
                "category": suggested_win["category"],
                "estimated_minutes": suggested_win["estimated_minutes"],
                "is_custom": False,
                "usage_count": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Save suggested win
            response = supabase.table("wins").insert(win_data).execute()
            if response.data:
                win_responses.append(WinResponse(**response.data[0]))
        
        return win_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}"
        )

@router.post("/complete", response_model=WinCompletionResponse, status_code=status.HTTP_201_CREATED)
async def complete_win(
    completion: WinCompletionCreate,
    current_user: str = Depends(get_current_user)
):
    """Complete a win and update streak"""
    try:
        supabase = get_supabase()
        
        # Verify win exists and belongs to user
        win_response = supabase.table("wins").select("*").eq(
            "id", str(completion.win_id)
        ).eq("user_id", current_user).execute()
        
        if not win_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Win not found"
            )
        
        # Create completion record
        completion_data = {
            "id": str(uuid4()),
            "user_id": current_user,
            "win_id": str(completion.win_id),
            "reflection_id": str(completion.reflection_id) if completion.reflection_id else None,
            "completed_at": datetime.utcnow().isoformat(),
            "notes": completion.notes,
            "mood_after": completion.mood_after
        }
        
        response = supabase.table("win_completions").insert(completion_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record completion"
            )
        
        # Update win usage count and last used
        supabase.table("wins").update({
            "usage_count": win_response.data[0]["usage_count"] + 1,
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("id", str(completion.win_id)).execute()
        
        # Update user streak (using database function)
        supabase.rpc("update_user_streak", {"p_user_id": current_user}).execute()
        
        return WinCompletionResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/", response_model=List[WinResponse])
async def get_user_wins(
    current_user: str = Depends(get_current_user),
    custom_only: bool = False,
    limit: int = 50,
    offset: int = 0
):
    """Get user's wins (custom wins and/or suggested wins)"""
    try:
        supabase = get_supabase()
        
        query = supabase.table("wins").select("*").eq("user_id", current_user)
        
        if custom_only:
            query = query.eq("is_custom", True)
        
        response = query.order("last_used_at", desc=True, nulls_first=False).order(
            "created_at", desc=True
        ).range(offset, offset + limit - 1).execute()
        
        return [WinResponse(**item) for item in response.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/completions", response_model=List[WinCompletionResponse])
async def get_win_completions(
    current_user: str = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's win completion history"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("win_completions").select("*").eq(
            "user_id", current_user
        ).order("completed_at", desc=True).range(
            offset, offset + limit - 1
        ).execute()
        
        return [WinCompletionResponse(**item) for item in response.data]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )