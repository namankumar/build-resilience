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

@router.get("/suggest", response_model=List[WinResponse])
async def get_suggested_wins_get(
    reflection_id: str,
    mood: int = 5,
    exclude_recent: bool = True,
    current_user: str = Depends(get_current_user)
):
    """Get AI-suggested wins based on reflection (GET version for frontend)"""
    try:
        from uuid import UUID
        
        # Create request object from query parameters
        request = WinSuggestionRequest(
            reflection_id=UUID(reflection_id),
            mood_intensity=mood,
            exclude_recent=exclude_recent
        )
        
        # Call the main suggestion logic
        return await generate_suggested_wins_logic(request, current_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}"
        )

@router.post("/suggest", response_model=List[WinResponse])
async def get_suggested_wins_post(
    request: WinSuggestionRequest,
    current_user: str = Depends(get_current_user)
):
    """Get AI-suggested wins based on reflection (POST version)"""
    return await generate_suggested_wins_logic(request, current_user)

async def generate_suggested_wins_logic(
    request: WinSuggestionRequest,
    current_user: str
):
    """Shared logic for generating suggested wins"""
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
                "win_id"
            ).eq("user_id", current_user).order(
                "completed_at", desc=True
            ).limit(10).execute()
            
            # Get win details for context
            if completions_response.data:
                win_ids = [comp["win_id"] for comp in completions_response.data]
                wins_response = supabase.table("wins").select("title, category").in_(
                    "id", win_ids
                ).execute()
                
                past_wins = [
                    f"{win['title']} ({win['category']})" 
                    for win in wins_response.data
                ]
        
        # Generate AI suggestions (with fallback)
        try:
            win_generator = WinGeneratorAgent()
            suggested_wins = await win_generator.generate_wins(
                reflection["content"],
                mood_intensity=request.mood_intensity or reflection.get("mood_intensity"),
                user_context={"past_successful_wins": past_wins}
            )
        except Exception as ai_error:
            print(f"⚠️  AI service unavailable, using fallback wins: {ai_error}")
            # Fallback to predefined wins based on mood
            mood_intensity = request.mood_intensity or reflection.get("mood_intensity", 5)
            suggested_wins = get_fallback_wins(mood_intensity)
        
        # Convert to WinResponse format and save as system wins
        win_responses = []
        for suggested_win in suggested_wins:
            win_data = {
                "user_id": current_user,
                "title": suggested_win["title"],
                "description": suggested_win["description"],
                "category": suggested_win["category"],
                "estimated_minutes": suggested_win["estimated_minutes"],
                "is_custom": False,
                "usage_count": 0
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

def get_fallback_wins(mood_intensity: int):
    """Fallback wins when AI service is unavailable"""
    if mood_intensity <= 3:
        # Low mood - gentle activities
        return [
            {
                "title": "Take 5 deep breaths",
                "description": "Focus on slow, calming breaths to center yourself",
                "category": "mindfulness",
                "estimated_minutes": 3
            },
            {
                "title": "Listen to a favorite song",
                "description": "Put on something that brings you comfort",
                "category": "self-care", 
                "estimated_minutes": 5
            },
            {
                "title": "Write down one thing you're grateful for",
                "description": "Find something small to appreciate today",
                "category": "mindfulness",
                "estimated_minutes": 2
            }
        ]
    elif mood_intensity <= 6:
        # Neutral mood - balanced activities
        return [
            {
                "title": "Take a 10-minute walk",
                "description": "Get some fresh air and light movement",
                "category": "movement",
                "estimated_minutes": 10
            },
            {
                "title": "Organize one small space",
                "description": "Tidy up your desk or a drawer",
                "category": "productivity",
                "estimated_minutes": 15
            },
            {
                "title": "Call or text a friend",
                "description": "Reach out to someone you care about",
                "category": "connection",
                "estimated_minutes": 10
            }
        ]
    else:
        # Good mood - more energetic activities
        return [
            {
                "title": "Do 20 jumping jacks",
                "description": "Get your blood flowing with quick exercise",
                "category": "movement",
                "estimated_minutes": 5
            },
            {
                "title": "Plan something fun for this week",
                "description": "Schedule an activity you're looking forward to",
                "category": "productivity",
                "estimated_minutes": 10
            },
            {
                "title": "Learn something new for 10 minutes",
                "description": "Watch a tutorial or read about a topic you're curious about",
                "category": "learning",
                "estimated_minutes": 10
            }
        ]

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
        current_usage = win_response.data[0].get("usage_count", 0) or 0
        supabase.table("wins").update({
            "usage_count": current_usage + 1,
            "last_used_at": datetime.utcnow().isoformat()
        }).eq("id", str(completion.win_id)).execute()
        
        # Update user streak (manual implementation since function doesn't exist)
        try:
            # Get or create streak record
            streak_response = supabase.table("streaks").select("*").eq(
                "user_id", current_user
            ).execute()
            
            if streak_response.data:
                # Update existing streak
                current_streak = streak_response.data[0]["current_streak"] + 1
                longest_streak = max(streak_response.data[0]["longest_streak"], current_streak)
                
                supabase.table("streaks").update({
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "last_activity_date": datetime.utcnow().date().isoformat()
                }).eq("user_id", current_user).execute()
            else:
                # Create initial streak
                supabase.table("streaks").insert({
                    "user_id": current_user,
                    "current_streak": 1,
                    "longest_streak": 1,
                    "last_activity_date": datetime.utcnow().date().isoformat()
                }).execute()
        except Exception as streak_error:
            # Don't fail the entire completion if streak update fails
            print(f"⚠️  Streak update failed: {streak_error}")
        
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
        
        response = query.order("last_used_at", desc=True).order(
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

@router.get("/{win_id}", response_model=WinResponse)
async def get_win_by_id(
    win_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific win by ID"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("wins").select("*").eq("id", win_id).eq(
            "user_id", current_user
        ).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Win not found"
            )
        
        return WinResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/completions/{completion_id}", response_model=WinCompletionResponse)
async def get_win_completion_by_id(
    completion_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific win completion by ID"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("win_completions").select("*").eq("id", completion_id).eq(
            "user_id", current_user
        ).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Win completion not found"
            )
        
        return WinCompletionResponse(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )