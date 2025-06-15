from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class WinCategory(str, Enum):
    MOVEMENT = "movement"
    MINDFULNESS = "mindfulness"
    CONNECTION = "connection"
    SELF_CARE = "self-care"
    PRODUCTIVITY = "productivity"

class WinCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: WinCategory
    estimated_minutes: int = Field(..., ge=1, le=60)
    is_custom: bool = True

class WinResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    category: WinCategory
    estimated_minutes: int
    is_custom: bool
    usage_count: int
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class WinCompletionCreate(BaseModel):
    win_id: UUID
    reflection_id: Optional[UUID] = None
    notes: Optional[str] = Field(None, max_length=500)
    mood_after: Optional[int] = Field(None, ge=1, le=10)

class WinCompletionResponse(BaseModel):
    id: UUID
    win_id: UUID
    reflection_id: Optional[UUID]
    completed_at: datetime
    notes: Optional[str]
    mood_after: Optional[int]
    
    class Config:
        from_attributes = True

class WinSuggestionRequest(BaseModel):
    reflection_id: UUID
    mood_intensity: Optional[int] = Field(None, ge=1, le=10)
    exclude_recent: bool = True