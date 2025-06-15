import anthropic
from typing import Dict, Any, Optional
from app.services.ai.base_agent import BaseAgent, AIModel
from app.core.config import settings

class ReframeAgent(BaseAgent):
    def __init__(self):
        super().__init__(AIModel.CLAUDE_HAIKU, max_tokens=500)
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    def get_system_prompt(self) -> str:
        return """You are a compassionate AI assistant helping someone process difficult emotions or slip-ups. Your role is to:

1. VALIDATE their feelings without judgment
2. DEFUSE shame and self-criticism gently
3. RECOGNIZE their resilience and strength
4. NORMALIZE their struggle as human experience

Guidelines:
- Keep responses to 2-4 sentences maximum
- Be warm, understanding, and non-judgmental
- Avoid toxic positivity or minimizing their feelings
- Don't give generic advice - respond to their specific situation
- Focus on their inherent worth and resilience
- Help them see this moment as part of their journey, not a failure

Remember: This person is vulnerable right now. Your words can either harm or heal."""

    async def generate_response(
        self, 
        reflection_content: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        user_prompt = f"Someone shared this with you: '{reflection_content}'"
        
        if context and context.get('mood_intensity'):
            mood_level = context['mood_intensity']
            if mood_level <= 3:
                user_prompt += f" They seem to be feeling quite low (intensity: {mood_level}/10)."
            elif mood_level >= 8:
                user_prompt += f" They seem quite distressed (intensity: {mood_level}/10)."
        
        try:
            response = self.client.messages.create(
                model=self.model.value,
                max_tokens=self.max_tokens,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            # Fallback response for API failures
            return "I hear you, and what you're experiencing is completely understandable. You're being brave by acknowledging these feelings. This moment doesn't define you - you have the strength to move through this."