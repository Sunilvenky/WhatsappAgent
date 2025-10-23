"""
AI-powered message rewriter to make messages sound natural and avoid spam detection.
"""
import logging
from typing import Optional, Dict, Any
from .llm_client import get_llm_client

logger = logging.getLogger(__name__)


class MessageRewriter:
    """
    Rewrites marketing messages to sound more natural and human-like.
    Helps avoid spam detection and improves engagement.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
    
    async def rewrite_message(
        self,
        original_message: str,
        contact_name: Optional[str] = None,
        tone: str = "friendly",
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Rewrite a message to sound more natural and engaging.
        
        Args:
            original_message: Original marketing message
            contact_name: Recipient's name for personalization
            tone: Desired tone (friendly, professional, casual, formal)
            context: Additional context (e.g., previous conversations, contact info)
            
        Returns:
            Rewritten message
        """
        system_prompt = """You are an expert WhatsApp message writer. Your job is to rewrite marketing messages to:
1. Sound natural and conversational (like a real person texting)
2. Avoid spam trigger words
3. Be engaging and personalized
4. Keep it concise (under 200 words)
5. Use appropriate emojis sparingly (1-2 max)
6. Match the requested tone

IMPORTANT: 
- Do NOT use overly salesy language
- Do NOT use all caps or excessive punctuation
- Do NOT make promises that weren't in the original
- Keep the core message and call-to-action intact
- Use WhatsApp-friendly formatting (no markdown)
"""
        
        context_str = ""
        if contact_name:
            context_str += f"Recipient's name: {contact_name}\n"
        if context:
            context_str += f"Additional context: {context}\n"
        
        prompt = f"""Original message:
{original_message}

{context_str}
Desired tone: {tone}

Rewrite this message to be more natural and engaging while maintaining the core message. Output ONLY the rewritten message, nothing else."""
        
        try:
            rewritten = await self.llm.complete(
                prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=300
            )
            
            # Log rewriting for monitoring
            logger.info(f"Message rewritten: {len(original_message)} -> {len(rewritten)} chars")
            
            return rewritten.strip()
            
        except Exception as e:
            logger.error(f"Message rewriting failed: {e}")
            # Fallback to original message if rewriting fails
            return original_message
    
    async def rewrite_batch(
        self,
        messages: list[str],
        tone: str = "friendly",
    ) -> list[str]:
        """
        Rewrite multiple messages in batch.
        
        Args:
            messages: List of original messages
            tone: Desired tone for all messages
            
        Returns:
            List of rewritten messages
        """
        import asyncio
        
        tasks = [
            self.rewrite_message(msg, tone=tone)
            for msg in messages
        ]
        
        return await asyncio.gather(*tasks)
    
    async def suggest_alternatives(
        self,
        original_message: str,
        num_alternatives: int = 3,
    ) -> list[str]:
        """
        Generate multiple alternative versions of a message.
        
        Args:
            original_message: Original message
            num_alternatives: Number of alternatives to generate
            
        Returns:
            List of alternative message versions
        """
        system_prompt = """You are an expert WhatsApp message writer. Generate multiple alternative versions of the given message.
Each version should:
- Sound natural and conversational
- Be different from the others (vary tone, structure, approach)
- Keep the core message intact
- Be concise and engaging
"""
        
        prompt = f"""Generate {num_alternatives} alternative versions of this message:

{original_message}

Output as JSON array of strings:
["version 1", "version 2", "version 3"]
"""
        
        try:
            result = await self.llm.complete_json(prompt, system_prompt=system_prompt)
            
            if isinstance(result, list):
                return result[:num_alternatives]
            elif isinstance(result, dict) and "alternatives" in result:
                return result["alternatives"][:num_alternatives]
            else:
                logger.warning(f"Unexpected result format: {result}")
                return [original_message]
                
        except Exception as e:
            logger.error(f"Alternative generation failed: {e}")
            return [original_message]
    
    async def check_spam_risk(self, message: str) -> Dict[str, Any]:
        """
        Analyze message for spam risk factors.
        
        Args:
            message: Message to analyze
            
        Returns:
            Dict with risk_score (0-100), risk_level (low/medium/high), and issues found
        """
        system_prompt = """You are a spam detection expert. Analyze the message for spam indicators:
- Excessive caps, exclamation marks, or emojis
- Spam trigger words (FREE, URGENT, LIMITED TIME, CALL NOW, etc.)
- Suspicious links or shortened URLs
- Overly promotional language
- Grammatical errors or typos

Rate the spam risk 0-100 and identify specific issues."""
        
        prompt = f"""Analyze this WhatsApp message for spam risk:

{message}

Respond in JSON format:
{{
    "risk_score": 0-100,
    "risk_level": "low|medium|high",
    "issues": ["issue 1", "issue 2"],
    "suggestions": ["suggestion 1", "suggestion 2"]
}}
"""
        
        try:
            result = await self.llm.complete_json(prompt, system_prompt=system_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Spam risk check failed: {e}")
            return {
                "risk_score": 0,
                "risk_level": "unknown",
                "issues": [],
                "suggestions": []
            }
