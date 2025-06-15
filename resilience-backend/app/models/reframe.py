from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ReframeRequest(BaseModel):
    reflection_id: UUID
    user_context: Optional[Dict[str, Any]] = None

class ReframeResponse(BaseModel):
    id: UUID
    reflection_id: UUID
    content: str
    ai_model_used: str
    created_at: datetime
    saved: bool = False
    
    class Config:
        from_attributes = True

class ReframeSaveRequest(BaseModel):
    reframe_id: UUID
    save: bool = True