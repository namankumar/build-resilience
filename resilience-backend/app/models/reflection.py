from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class ReflectionCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    mood_emoji: Optional[str] = None
    mood_intensity: Optional[int] = Field(None, ge=1, le=10)

class ReflectionResponse(BaseModel):
    id: UUID
    content: str
    mood_emoji: Optional[str]
    mood_intensity: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReflectionUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    mood_emoji: Optional[str] = None
    mood_intensity: Optional[int] = Field(None, ge=1, le=10)