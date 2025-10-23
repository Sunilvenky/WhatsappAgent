"""
AI-powered reply classifier for categorizing incoming WhatsApp messages.
"""
import logging
from typing import Dict, Any, Optional
from enum import Enum
from .llm_client import get_llm_client

logger = logging.getLogger(__name__)


class ReplyIntent(str, Enum):
    """Reply intent categories."""
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    QUESTION = "question"
    UNSUBSCRIBE = "unsubscribe"
    OUT_OF_OFFICE = "out_of_office"
    COMPLAINT = "complaint"
    POSITIVE_FEEDBACK = "positive_feedback"
    NEEDS_HUMAN = "needs_human"
    UNKNOWN = "unknown"


class ReplySentiment(str, Enum):
    """Reply sentiment."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ReplyClassifier:
    """
    Classifies incoming message replies to determine intent and sentiment.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
    
    async def classify_reply(
        self,
        reply_text: str,
        original_message: Optional[str] = None,
        conversation_history: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """
        Classify an incoming reply message.
        
        Args:
            reply_text: The reply message to classify
            original_message: The original message that was sent
            conversation_history: Previous messages in conversation
            
        Returns:
            Classification result with intent, sentiment, confidence, and suggested action
        """
        system_prompt = """You are an expert at analyzing WhatsApp message replies to marketing/sales messages.
Classify the reply into one of these intents:
- interested: Shows interest, wants to know more, positive response
- not_interested: Clearly not interested, rejection, dismissal
- question: Asking for clarification, more information, or has concerns
- unsubscribe: Wants to stop receiving messages (STOP, unsubscribe, remove me, etc.)
- out_of_office: Auto-reply indicating unavailability
- complaint: Complaining about receiving messages or content
- positive_feedback: Thanking, praising, or positive feedback
- needs_human: Complex query that needs human attention
- unknown: Cannot determine intent

Also determine sentiment (positive, neutral, negative) and confidence level (0-100)."""
        
        context_str = ""
        if original_message:
            context_str += f"Original message sent:\n{original_message}\n\n"
        if conversation_history:
            context_str += "Previous conversation:\n" + "\n".join(conversation_history) + "\n\n"
        
        prompt = f"""{context_str}Reply received:
{reply_text}

Classify this reply and respond in JSON format:
{{
    "intent": "interested|not_interested|question|unsubscribe|out_of_office|complaint|positive_feedback|needs_human|unknown",
    "sentiment": "positive|neutral|negative",
    "confidence": 0-100,
    "key_phrases": ["phrase1", "phrase2"],
    "suggested_action": "Description of what to do next",
    "urgency": "low|medium|high",
    "reasoning": "Brief explanation"
}}
"""
        
        try:
            result = await self.llm.complete_json(prompt, system_prompt=system_prompt)
            
            # Validate and normalize result
            result["intent"] = result.get("intent", "unknown").lower()
            result["sentiment"] = result.get("sentiment", "neutral").lower()
            result["confidence"] = min(100, max(0, result.get("confidence", 0)))
            
            logger.info(f"Classified reply: intent={result['intent']}, confidence={result['confidence']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Reply classification failed: {e}")
            return {
                "intent": "unknown",
                "sentiment": "neutral",
                "confidence": 0,
                "key_phrases": [],
                "suggested_action": "Manual review required",
                "urgency": "low",
                "reasoning": f"Classification error: {str(e)}"
            }
    
    async def classify_batch(
        self,
        replies: list[Dict[str, str]],
    ) -> list[Dict[str, Any]]:
        """
        Classify multiple replies in batch.
        
        Args:
            replies: List of dicts with 'text' and optionally 'original_message'
            
        Returns:
            List of classification results
        """
        import asyncio
        
        tasks = [
            self.classify_reply(
                reply.get("text", ""),
                original_message=reply.get("original_message")
            )
            for reply in replies
        ]
        
        return await asyncio.gather(*tasks)
    
    async def extract_intent_keywords(self, reply_text: str) -> list[str]:
        """
        Extract key intent-revealing keywords from reply.
        
        Args:
            reply_text: Reply message
            
        Returns:
            List of intent keywords
        """
        system_prompt = "Extract key words or phrases that indicate the user's intent from this WhatsApp reply."
        
        prompt = f"""Reply: {reply_text}

Extract 3-5 key words or phrases that best represent the user's intent.
Respond as JSON array: ["keyword1", "keyword2", ...]
"""
        
        try:
            result = await self.llm.complete_json(prompt, system_prompt=system_prompt)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "keywords" in result:
                return result["keywords"]
            return []
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    async def should_auto_respond(
        self,
        classification: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Determine if message should get auto-response and suggest response.
        
        Args:
            classification: Result from classify_reply()
            
        Returns:
            Dict with should_respond (bool), suggested_response (str), and reasoning
        """
        intent = classification.get("intent", "unknown")
        sentiment = classification.get("sentiment", "neutral")
        confidence = classification.get("confidence", 0)
        
        # Auto-response rules
        should_respond = False
        suggested_response = ""
        reasoning = ""
        
        if intent == ReplyIntent.UNSUBSCRIBE:
            should_respond = True
            suggested_response = "Understood, you've been removed from our list. You won't receive further messages from us."
            reasoning = "Unsubscribe request - confirm removal"
            
        elif intent == ReplyIntent.OUT_OF_OFFICE:
            should_respond = False
            reasoning = "Auto-reply detected - skip response"
            
        elif intent == ReplyIntent.INTERESTED and confidence > 70:
            should_respond = True
            system_prompt = "Generate a brief, friendly response to continue the conversation with an interested lead."
            prompt = f"The user replied: {classification.get('key_phrases', [])}\nSuggest a short follow-up message (1-2 sentences)."
            try:
                suggested_response = await self.llm.complete(prompt, system_prompt=system_prompt, max_tokens=100)
                reasoning = "High-confidence interest - engage further"
            except:
                suggested_response = "Great to hear from you! Let me know if you have any questions."
                
        elif intent == ReplyIntent.QUESTION:
            should_respond = False
            reasoning = "Question detected - needs human attention"
            suggested_response = "Flag for human review"
            
        elif intent == ReplyIntent.COMPLAINT:
            should_respond = True
            suggested_response = "I apologize for any inconvenience. This has been flagged for immediate attention from our team."
            reasoning = "Complaint - acknowledge and escalate"
            
        elif intent == ReplyIntent.POSITIVE_FEEDBACK:
            should_respond = True
            suggested_response = "Thank you so much for your kind words! We really appreciate your feedback. 😊"
            reasoning = "Positive feedback - express gratitude"
        
        return {
            "should_respond": should_respond,
            "suggested_response": suggested_response,
            "reasoning": reasoning,
            "requires_human_review": intent in [
                ReplyIntent.NEEDS_HUMAN,
                ReplyIntent.QUESTION,
                ReplyIntent.COMPLAINT
            ] or (intent == ReplyIntent.INTERESTED and confidence < 70)
        }
