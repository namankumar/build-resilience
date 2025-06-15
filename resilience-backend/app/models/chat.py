from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class ChatMode(str, Enum):
    LISTEN = "listen"
    NUDGE = "nudge"

class ChatStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class ChatSessionCreate(BaseModel):
    reflection_id: UUID

class ChatSessionResponse(BaseModel):
    id: UUID
    reflection_id: UUID
    status: ChatStatus
    current_mode: ChatMode
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    session_id: UUID
    message: str = Field(..., min_length=1, max_length=2000)

class ChatMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str  # 'user' or 'assistant'
    content: str
    ai_model_used: Optional[str]
    mood_analysis: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    message: ChatMessageResponse
    session_status: ChatStatus
    current_mode: ChatMode
    should_conclude: bool = False
    conclusion_suggestion: Optional[str] = None