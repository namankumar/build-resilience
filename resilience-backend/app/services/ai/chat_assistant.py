import anthropic
from typing import Dict, Any, List, Optional
from app.services.ai.base_agent import BaseAgent, AIModel
from app.services.ai.mood_detector import MoodDetectionAgent, MoodAnalysis
from app.core.config import settings

class ChatAssistantAgent(BaseAgent):
    def __init__(self):
        super().__init__(AIModel.CLAUDE_SONNET, max_tokens=800)
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.mood_detector = MoodDetectionAgent()
    
    def get_listen_mode_prompt(self) -> str:
        return """You are a compassionate therapist providing deep listening and emotional validation. Your role is to:

1. DEEPLY LISTEN and validate their feelings
2. ASK GENTLE QUESTIONS to help them process
3. REFLECT back what you hear
4. PROVIDE SPACE for their emotions
5. HELP them explore their feelings safely

Guidelines for Listen Mode:
- Use empathetic, validating language
- Ask open-ended questions about their experience
- Reflect their emotions back to them
- Don't rush to solutions or advice
- Help them feel heard and understood
- Allow for silence and processing
- Normalize their struggle

Remember: Your job is to create a safe space for them to process their emotions fully."""

    def get_nudge_mode_prompt(self) -> str:
        return """You are a gentle coach helping someone transition from processing emotions to taking small forward steps. Your role is to:

1. ACKNOWLEDGE their processing journey
2. GENTLY BRIDGE to action thinking
3. SUGGEST small, manageable steps
4. BUILD their confidence and energy
5. MAINTAIN warmth while encouraging movement

Guidelines for Nudge Mode:
- Honor the emotional work they've done
- Suggest rather than demand action
- Keep suggestions very small and doable
- Focus on their strengths and capabilities
- Maintain supportive, encouraging tone
- Help them see progress possibilities
- Offer choices rather than directives

Remember: You're helping them move from reflection to gentle action while maintaining full emotional support."""

    async def respond_to_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        current_mode: str = "listen"
    ) -> Dict[str, Any]:
        """Generate contextual response based on current mode and conversation analysis"""
        
        # Analyze conversation to determine appropriate mode
        mood_analysis = await self.mood_detector.analyze_conversation(
            conversation_history, message
        )
        
        # Determine response mode
        if mood_analysis.should_listen and mood_analysis.confidence_score > 0.7:
            response_mode = "listen"
        elif not mood_analysis.should_listen and mood_analysis.confidence_score > 0.7:
            response_mode = "nudge"
        else:
            # Keep current mode if analysis is uncertain
            response_mode = current_mode
        
        # Generate response based on mode
        if response_mode == "listen":
            system_prompt = self.get_listen_mode_prompt()
        else:
            system_prompt = self.get_nudge_mode_prompt()
        
        # Format conversation history
        formatted_history = []
        for msg in conversation_history[-8:]:  # Keep last 8 messages for context
            formatted_history.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })
        
        # Add current message
        formatted_history.append({"role": "user", "content": message})
        
        try:
            response = self.client.messages.create(
                model=self.model.value,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=formatted_history
            )
            
            return {
                "content": response.content[0].text,
                "mode": response_mode,
                "mood_analysis": {
                    "emotional_intensity": mood_analysis.emotional_intensity,
                    "processing_stage": mood_analysis.processing_stage,
                    "confidence_score": mood_analysis.confidence_score,
                    "reasoning": mood_analysis.reasoning
                }
            }
            
        except Exception as e:
            # Fallback response
            if response_mode == "listen":
                fallback_content = "I can hear that you're going through something difficult right now. Would you like to share more about what you're feeling?"
            else:
                fallback_content = "It sounds like you've been processing a lot. What feels like a small step you could take right now?"
            
            return {
                "content": fallback_content,
                "mode": response_mode,
                "mood_analysis": {
                    "emotional_intensity": 5,
                    "processing_stage": "processing",
                    "confidence_score": 0.3,
                    "reasoning": "Fallback response due to API error"
                }
            }

    async def should_conclude_conversation(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Determine if conversation should naturally conclude"""
        
        if len(conversation_history) < 4:
            return {"should_conclude": False, "reason": "Conversation too brief"}
        
        # Check if user is showing signs of readiness to end
        recent_messages = conversation_history[-3:]
        user_messages = [msg["content"] for msg in recent_messages if msg["role"] == "user"]
        
        conclusion_signals = [
            "thank you", "that helps", "feeling better", "i think i'm ready",
            "that's helpful", "i should go", "i feel more", "makes sense"
        ]
        
        for message in user_messages:
            if any(signal in message.lower() for signal in conclusion_signals):
                return {
                    "should_conclude": True,
                    "reason": "User showing readiness to conclude",
                    "suggested_closing": "I'm glad this conversation has been helpful. Remember, you have the strength to handle whatever comes next. Take care of yourself."
                }
        
        # Check if conversation has been very long (>15 exchanges)
        if len(conversation_history) > 15:
            return {
                "should_conclude": True,
                "reason": "Extended conversation - suggest natural break",
                "suggested_closing": "We've covered a lot of ground together. How are you feeling right now? Sometimes it's good to take a pause and let things settle."
            }
        
        return {"should_conclude": False, "reason": "Conversation can continue"}