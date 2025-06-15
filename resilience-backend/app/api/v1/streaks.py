from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.core.security import get_current_user
from app.core.database import get_supabase
from datetime import datetime, date

router = APIRouter(prefix="/streaks", tags=["streaks"])

@router.get("/current")
async def get_current_streak(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's current streak information"""
    try:
        supabase = get_supabase()
        
        # Get or create streak record
        response = supabase.table("streaks").select("*").eq(
            "user_id", current_user
        ).execute()
        
        if not response.data:
            # Create initial streak record
            streak_data = {
                "user_id": current_user,
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "streak_type": "daily"
            }
            
            create_response = supabase.table("streaks").insert(streak_data).execute()
            if create_response.data:
                streak = create_response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create streak record"
                )
        else:
            streak = response.data[0]
        
        # Calculate days since last activity
        days_since_activity = None
        if streak.get("last_activity_date"):
            last_date = datetime.fromisoformat(streak["last_activity_date"]).date()
            days_since_activity = (date.today() - last_date).days
        
        return {
            "current_streak": streak["current_streak"],
            "longest_streak": streak["longest_streak"],
            "last_activity_date": streak["last_activity_date"],
            "days_since_activity": days_since_activity,
            "streak_type": streak["streak_type"],
            "is_active": days_since_activity is not None and days_since_activity <= 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/history")
async def get_streak_history(
    current_user: str = Depends(get_current_user),
    days: int = 30
) -> Dict[str, Any]:
    """Get streak activity history for visualization"""
    try:
        supabase = get_supabase()
        
        # Get recent win completions for activity calendar
        end_date = date.today()
        start_date = date.today().replace(day=1)  # Start of current month
        
        response = supabase.table("win_completions").select(
            "completed_at"
        ).eq("user_id", current_user).gte(
            "completed_at", start_date.isoformat()
        ).lte(
            "completed_at", end_date.isoformat()
        ).execute()
        
        # Process activity data
        activity_dates = set()
        for completion in response.data:
            completion_date = datetime.fromisoformat(
                completion["completed_at"]
            ).date()
            activity_dates.add(completion_date.isoformat())
        
        # Get current streak info
        streak_response = supabase.table("streaks").select("*").eq(
            "user_id", current_user
        ).execute()
        
        streak_info = streak_response.data[0] if streak_response.data else {
            "current_streak": 0,
            "longest_streak": 0
        }
        
        return {
            "activity_dates": list(activity_dates),
            "current_streak": streak_info["current_streak"],
            "longest_streak": streak_info["longest_streak"],
            "total_activities": len(response.data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )