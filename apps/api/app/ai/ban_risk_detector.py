"""
AI-powered WhatsApp ban risk detection system.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .llm_client import get_llm_client

logger = logging.getLogger(__name__)


class BanRiskLevel(str):
    """Ban risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BanRiskDetector:
    """
    Detects patterns and behaviors that could lead to WhatsApp account bans.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
    
    async def analyze_message_pattern(
        self,
        messages_sent: List[Dict[str, Any]],
        time_window_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Analyze message sending patterns for ban risk.
        
        Args:
            messages_sent: List of recently sent messages with timestamps
            time_window_hours: Time window to analyze
            
        Returns:
            Risk analysis with score, level, and recommendations
        """
        if not messages_sent:
            return {
                "risk_score": 0,
                "risk_level": BanRiskLevel.LOW,
                "factors": [],
                "recommendations": []
            }
        
        # Calculate metrics
        total_messages = len(messages_sent)
        time_window = timedelta(hours=time_window_hours)
        now = datetime.utcnow()
        recent_messages = [
            m for m in messages_sent
            if (now - m.get("sent_at", now)) <= time_window
        ]
        
        messages_per_hour = len(recent_messages) / time_window_hours
        
        # Check for spam indicators
        risk_factors = []
        risk_score = 0
        
        # High message volume
        if messages_per_hour > 100:
            risk_factors.append("Very high message volume (>100/hour)")
            risk_score += 40
        elif messages_per_hour > 50:
            risk_factors.append("High message volume (>50/hour)")
            risk_score += 25
        
        # Check message similarity (spam indicator)
        if len(recent_messages) >= 5:
            texts = [m.get("text", "") for m in recent_messages[:20]]
            similarity_score = await self._calculate_message_similarity(texts)
            if similarity_score > 0.8:
                risk_factors.append(f"Very similar messages detected ({similarity_score:.0%} similarity)")
                risk_score += 30
            elif similarity_score > 0.6:
                risk_factors.append(f"Somewhat similar messages ({similarity_score:.0%} similarity)")
                risk_score += 15
        
        # Check response rate (low engagement = higher risk)
        replied_count = sum(1 for m in recent_messages if m.get("replied", False))
        if total_messages > 10:
            response_rate = replied_count / len(recent_messages)
            if response_rate < 0.05:
                risk_factors.append(f"Very low response rate ({response_rate:.1%})")
                risk_score += 25
            elif response_rate < 0.15:
                risk_factors.append(f"Low response rate ({response_rate:.1%})")
                risk_score += 10
        
        # Check for blocks/reports
        blocked_count = sum(1 for m in recent_messages if m.get("blocked", False))
        if blocked_count > 0:
            risk_factors.append(f"{blocked_count} contacts blocked you")
            risk_score += blocked_count * 20
        
        # Check message timing (too fast = bot-like)
        if len(recent_messages) >= 2:
            timestamps = sorted([m.get("sent_at", now) for m in recent_messages])
            avg_delay = sum(
                (timestamps[i+1] - timestamps[i]).total_seconds()
                for i in range(len(timestamps)-1)
            ) / (len(timestamps) - 1)
            
            if avg_delay < 1:
                risk_factors.append("Messages sent too quickly (<1s between messages)")
                risk_score += 35
            elif avg_delay < 2:
                risk_factors.append("Fast message sending (<2s between messages)")
                risk_score += 20
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = BanRiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = BanRiskLevel.HIGH
        elif risk_score >= 30:
            risk_level = BanRiskLevel.MEDIUM
        else:
            risk_level = BanRiskLevel.LOW
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, risk_score)
        
        return {
            "risk_score": min(100, risk_score),
            "risk_level": risk_level,
            "factors": risk_factors,
            "recommendations": recommendations,
            "metrics": {
                "total_messages": total_messages,
                "messages_per_hour": round(messages_per_hour, 2),
                "response_rate": round(replied_count / len(recent_messages), 2) if recent_messages else 0,
                "blocked_count": blocked_count,
            }
        }
    
    async def _calculate_message_similarity(self, texts: List[str]) -> float:
        """Calculate average similarity between messages (0-1)."""
        if len(texts) < 2:
            return 0.0
        
        try:
            # Use LLM to assess similarity
            system_prompt = "You are an expert at detecting spam patterns in text messages."
            prompt = f"""Analyze these messages and rate how similar they are (0-100):

{chr(10).join(f"{i+1}. {text[:100]}" for i, text in enumerate(texts[:10]))}

Respond ONLY with a number 0-100 indicating similarity percentage.
100 = identical/templates with minor changes
0 = completely different messages
"""
            
            result = await self.llm.complete(
                prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=10
            )
            
            # Extract number
            import re
            match = re.search(r'\d+', result)
            if match:
                return min(100, max(0, int(match.group()))) / 100
            return 0.5
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            # Fallback: simple text comparison
            unique_ratio = len(set(texts)) / len(texts)
            return 1.0 - unique_ratio
    
    def _generate_recommendations(
        self,
        risk_factors: List[str],
        risk_score: int
    ) -> List[str]:
        """Generate actionable recommendations based on risk factors."""
        recommendations = []
        
        if risk_score >= 60:
            recommendations.append("🚨 URGENT: Stop sending messages immediately for 24-48 hours")
            recommendations.append("Review and vary your message templates")
            recommendations.append("Enable number warmup protocol")
        
        if "message volume" in str(risk_factors).lower():
            recommendations.append("Reduce message sending rate to <50/hour")
            recommendations.append("Implement longer delays between messages (3-5 seconds)")
        
        if "similar messages" in str(risk_factors).lower():
            recommendations.append("Use AI message rewriting for more variation")
            recommendations.append("Create 5+ different message templates")
            recommendations.append("Personalize messages with contact details")
        
        if "response rate" in str(risk_factors).lower():
            recommendations.append("Improve message quality and relevance")
            recommendations.append("Better target audience segmentation")
            recommendations.append("Test different message approaches")
        
        if "blocked" in str(risk_factors).lower():
            recommendations.append("Stop contacting users who blocked you")
            recommendations.append("Review message content for spam indicators")
            recommendations.append("Consider warming up a new number")
        
        if "too quickly" in str(risk_factors).lower():
            recommendations.append("Increase minimum delay between messages to 2-5 seconds")
            recommendations.append("Add random delays to seem more human")
            recommendations.append("Enable typing indicators before sending")
        
        if not recommendations:
            recommendations.append("✅ Current pattern looks safe")
            recommendations.append("Continue monitoring response rates")
            recommendations.append("Maintain message variation")
        
        return recommendations
    
    async def analyze_message_content(self, message: str) -> Dict[str, Any]:
        """
        Analyze message content for ban risk indicators.
        
        Args:
            message: Message content to analyze
            
        Returns:
            Analysis with spam indicators and risk assessment
        """
        system_prompt = """You are a WhatsApp spam detection expert. Analyze this message for ban risk factors:
- Spam keywords (FREE, URGENT, LIMITED, CLICK HERE, etc.)
- Suspicious URLs or shortened links
- Excessive caps, punctuation, or emojis
- Promotional/salesy language
- Misleading or deceptive content
- Content that violates WhatsApp policies
"""
        
        prompt = f"""Analyze this WhatsApp message for ban risk:

{message}

Respond in JSON format:
{{
    "risk_score": 0-100,
    "risk_level": "low|medium|high|critical",
    "spam_indicators": ["indicator1", "indicator2"],
    "policy_violations": ["violation1"],
    "suggestions": ["how to improve"],
    "reasoning": "explanation"
}}
"""
        
        try:
            result = await self.llm.complete_json(prompt, system_prompt=system_prompt)
            return result
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {
                "risk_score": 0,
                "risk_level": "unknown",
                "spam_indicators": [],
                "policy_violations": [],
                "suggestions": [],
                "reasoning": f"Analysis error: {str(e)}"
            }
