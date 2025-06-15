import anthropic
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from app.services.ai.base_agent import BaseAgent, AIModel
from app.core.config import settings

@dataclass
class MoodAnalysis:
    should_listen: bool
    confidence_score: float  # 0.0 to 1.0
    reasoning: str
    suggested_approach: str
    emotional_intensity: int  # 1-10 scale
    processing_stage: str  # 'initial', 'processing', 'plateau', 'ready'

class MoodDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(AIModel.CLAUDE_HAIKU, max_tokens=300)
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    
    def get_system_prompt(self) -> str:
        return """You are an expert at analyzing emotional states and conversation dynamics to determine when someone needs to be heard vs. when they're ready for gentle action guidance.

Analyze the conversation history and determine:

LISTEN MODE INDICATORS:
- High emotional intensity or distress
- Still processing/discovering new insights
- Seeking validation or understanding
- Recent breakthrough or emotional release
- Complex emotions being untangled

NUDGE MODE INDICATORS:
- Emotional intensity has stabilized
- Repetitive or circular thought patterns
- Natural energy shift toward action
- Expressing readiness signals
- Processing appears complete for now

Return your analysis in this exact JSON format:
{
    "should_listen": boolean,
    "confidence_score": float (0.0-1.0),
    "reasoning": "specific reasoning for decision",
    "suggested_approach": "specific guidance for response",
    "emotional_intensity": integer (1-10),
    "processing_stage": "initial|processing|plateau|ready"
}

Always err on the side of listening when uncertain."""

    async def analyze_conversation(
        self, 
        conversation_history: List[Dict[str, str]],
        current_message: str
    ) -> MoodAnalysis:
        # Format conversation for analysis
        formatted_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history[-10:]  # Last 10 messages for context
        ])
        
        user_prompt = f"""CONVERSATION HISTORY:
{formatted_history}

CURRENT MESSAGE: {current_message}

Analyze this conversation to determine if the person needs continued listening support or if they're ready for gentle action guidance."""

        try:
            response = self.client.messages.create(
                model=self.model.value,
                max_tokens=self.max_tokens,
                system=self.get_system_prompt(),
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Parse JSON response
            analysis_data = json.loads(response.content[0].text)
            
            return MoodAnalysis(
                should_listen=analysis_data["should_listen"],
                confidence_score=analysis_data["confidence_score"],
                reasoning=analysis_data["reasoning"],
                suggested_approach=analysis_data["suggested_approach"],
                emotional_intensity=analysis_data["emotional_intensity"],
                processing_stage=analysis_data["processing_stage"]
            )
            
        except Exception as e:
            # Safe fallback - always listen when uncertain
            return MoodAnalysis(
                should_listen=True,
                confidence_score=0.3,
                reasoning="Error in analysis - defaulting to listening mode for safety",
                suggested_approach="Provide empathetic listening and validation",
                emotional_intensity=7,
                processing_stage="processing"
            )