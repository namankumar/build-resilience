import openai
import json
from typing import Dict, Any, List, Optional
from app.services.ai.base_agent import BaseAgent, AIModel
from app.core.config import settings

class WinGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(AIModel.GPT_4O_MINI, max_tokens=400)
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    def get_system_prompt(self) -> str:
        return """You are an expert at creating personalized micro-wins that help people recover from emotional setbacks. Your job is to suggest 1-2 small, achievable actions that:

1. Take 2-5 minutes maximum
2. Are immediately doable
3. Help rebuild positive momentum
4. Match the person's current emotional state
5. Feel like genuine wins, not chores

CATEGORIES:
- Movement: gentle physical activity
- Mindfulness: breathing, grounding exercises
- Connection: reaching out to others
- Self-care: nurturing activities
- Productivity: small organizing tasks

Guidelines:
- Make suggestions specific and actionable
- Consider their current mood and energy level
- Avoid overwhelming or demanding tasks
- Focus on identity-reinforcing actions
- Suggest wins they can do right now

Return exactly 1-2 wins in this JSON format:
{
    "wins": [
        {
            "title": "Short, clear title",
            "description": "Brief explanation of the action",
            "category": "movement|mindfulness|connection|self-care|productivity",
            "estimated_minutes": 2-5
        }
    ]
}"""

    async def generate_wins(
        self, 
        reflection_content: str,
        mood_intensity: Optional[int] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        
        user_prompt = f"Someone shared: '{reflection_content}'"
        
        if mood_intensity:
            if mood_intensity <= 3:
                user_prompt += f" They're feeling quite low (mood: {mood_intensity}/10). Suggest very gentle, nurturing wins."
            elif mood_intensity >= 8:
                user_prompt += f" They're highly distressed (mood: {mood_intensity}/10). Suggest calming, grounding wins."
            else:
                user_prompt += f" Their mood is moderate (mood: {mood_intensity}/10). Suggest energizing but manageable wins."
        
        if user_context and user_context.get('past_successful_wins'):
            user_prompt += f" They've previously found success with: {', '.join(user_context['past_successful_wins'])}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model.value,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse JSON response
            wins_data = json.loads(response.choices[0].message.content)
            return wins_data["wins"]
            
        except Exception as e:
            # Fallback wins based on mood
            if mood_intensity and mood_intensity <= 4:
                return [{
                    "title": "Take 3 deep breaths",
                    "description": "Breathe in for 4 counts, hold for 4, breathe out for 6",
                    "category": "mindfulness",
                    "estimated_minutes": 2
                }]
            else:
                return [{
                    "title": "Drink a glass of water mindfully",
                    "description": "Focus on the temperature and taste as you drink slowly",
                    "category": "self-care",
                    "estimated_minutes": 3
                }]