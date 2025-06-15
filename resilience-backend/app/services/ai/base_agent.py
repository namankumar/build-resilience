from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

class AIModel(Enum):
    CLAUDE_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    GPT_4O_MINI = "gpt-4o-mini"

class BaseAgent(ABC):
    def __init__(self, model: AIModel, max_tokens: int = 1000):
        self.model = model
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass