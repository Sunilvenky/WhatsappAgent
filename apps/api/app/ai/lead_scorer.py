"""
AI-powered lead scoring system.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .llm_client import get_llm_client

logger = logging.getLogger(__name__)


class LeadScorer:
    """
    Scores leads based on engagement, profile, and behavior using AI.
    """
    
    def __init__(self):
        self.llm = get_llm_client()
    
    async def score_lead(
        self,
        contact: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        engagement_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive lead score.
        
        Args:
            contact: Contact information (name, phone, metadata)
            conversation_history: List of messages exchanged
            engagement_data: Metrics like opens, clicks, responses
            
        Returns:
            Lead score (0-100), quality tier, and breakdown
        """
        # Initialize scores
        engagement_score = 0
        profile_score = 0
        behavior_score = 0
        timing_score = 0
        
        # 1. Engagement scoring (40% weight)
        if engagement_data:
            response_rate = engagement_data.get("response_rate", 0)
            engagement_score += response_rate * 25  # Max 25 points
            
            if engagement_data.get("clicked_links", 0) > 0:
                engagement_score += 10
            
            if engagement_data.get("opened_messages", 0) >= 3:
                engagement_score += 5
        
        # 2. Profile scoring (20% weight)
        if contact:
            if contact.get("name") and contact.get("name") != contact.get("phone"):
                profile_score += 5
            
            if contact.get("email"):
                profile_score += 5
            
            if contact.get("company"):
                profile_score += 5
            
            metadata = contact.get("metadata", {})
            if metadata.get("linkedin_profile"):
                profile_score += 5
        
        # 3. Behavior scoring (30% weight) - AI-powered
        if conversation_history:
            behavior_score = await self._analyze_conversation_behavior(conversation_history)
        
        # 4. Timing scoring (10% weight)
        timing_score = self._calculate_timing_score(conversation_history, engagement_data)
        
        # Calculate weighted total
        total_score = (
            engagement_score * 0.4 +
            profile_score * 0.2 +
            behavior_score * 0.3 +
            timing_score * 0.1
        )
        
        # Determine quality tier
        if total_score >= 80:
            quality_tier = "hot"
            priority = "high"
        elif total_score >= 60:
            quality_tier = "warm"
            priority = "medium"
        elif total_score >= 30:
            quality_tier = "cold"
            priority = "low"
        else:
            quality_tier = "inactive"
            priority = "very_low"
        
        # Generate insights
        insights = await self._generate_lead_insights(
            total_score,
            contact,
            conversation_history
        )
        
        return {
            "total_score": round(total_score, 2),
            "quality_tier": quality_tier,
            "priority": priority,
            "breakdown": {
                "engagement": round(engagement_score * 0.4, 2),
                "profile": round(profile_score * 0.2, 2),
                "behavior": round(behavior_score * 0.3, 2),
                "timing": round(timing_score * 0.1, 2),
            },
            "insights": insights,
            "next_actions": self._recommend_next_actions(quality_tier, insights),
        }
    
    async def _analyze_conversation_behavior(
        self,
        conversation_history: List[Dict[str, Any]]
    ) -> float:
        """Analyze conversation for behavioral signals using AI."""
        if not conversation_history:
            return 0.0
        
        # Format conversation
        conversation_text = "\n".join([
            f"{'User' if msg.get('from_contact') else 'Agent'}: {msg.get('text', '')[:100]}"
            for msg in conversation_history[:10]  # Last 10 messages
        ])
        
        system_prompt = """You are an expert sales lead analyzer. Evaluate conversation for buying signals:
- Questions about pricing, features, or implementation
- Positive sentiment and interest
- Urgency indicators
- Decision-making authority
- Engagement level
- Objections or concerns

Score 0-100 based on lead quality."""
        
        prompt = f"""Analyze this conversation and score the lead quality (0-100):

{conversation_text}

Respond in JSON format:
{{
    "behavior_score": 0-100,
    "buying_signals": ["signal1", "signal2"],
    "concerns": ["concern1"],
    "engagement_level": "low|medium|high",
    "reasoning": "brief explanation"
}}
"""
        
        try:
            result = await self.llm.complete_json(prompt, system_prompt=system_prompt)
            return min(100, max(0, result.get("behavior_score", 0)))
        except Exception as e:
            logger.error(f"Behavior analysis failed: {e}")
            # Fallback: count messages from contact
            contact_messages = sum(1 for m in conversation_history if m.get("from_contact"))
            return min(100, contact_messages * 20)
    
    def _calculate_timing_score(
        self,
        conversation_history: Optional[List[Dict[str, Any]]],
        engagement_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate score based on response timing and recency."""
        score = 0.0
        
        if not conversation_history:
            return score
        
        now = datetime.utcnow()
        
        # Recent activity bonus
        last_message = conversation_history[-1] if conversation_history else None
        if last_message:
            last_activity = last_message.get("timestamp", now)
            hours_since = (now - last_activity).total_seconds() / 3600
            
            if hours_since < 24:
                score += 50  # Very recent
            elif hours_since < 72:
                score += 30  # Recent
            elif hours_since < 168:  # 1 week
                score += 15
        
        # Fast response bonus
        if engagement_data and engagement_data.get("avg_response_time_minutes"):
            avg_response = engagement_data["avg_response_time_minutes"]
            if avg_response < 15:
                score += 30
            elif avg_response < 60:
                score += 20
            elif avg_response < 240:  # 4 hours
                score += 10
        
        return min(100, score)
    
    async def _generate_lead_insights(
        self,
        score: float,
        contact: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate actionable insights about the lead."""
        insights = []
        
        if score >= 80:
            insights.append("🔥 Highly engaged lead - prioritize immediate follow-up")
        elif score >= 60:
            insights.append("✅ Warm lead - good engagement, nurture relationship")
        elif score >= 30:
            insights.append("❄️ Cold lead - needs more engagement")
        else:
            insights.append("💤 Inactive lead - consider re-engagement campaign")
        
        # Analyze conversation if available
        if conversation_history and len(conversation_history) >= 3:
            try:
                # Get AI insights
                conv_text = "\n".join([
                    msg.get("text", "")[:100] for msg in conversation_history[-5:]
                ])
                
                system_prompt = "Extract 2-3 key insights about this lead from the conversation."
                prompt = f"Conversation:\n{conv_text}\n\nProvide insights as JSON array: [\"insight1\", \"insight2\"]"
                
                ai_insights = await self.llm.complete_json(prompt, system_prompt=system_prompt)
                if isinstance(ai_insights, list):
                    insights.extend(ai_insights[:3])
            except Exception as e:
                logger.error(f"AI insights generation failed: {e}")
        
        return insights
    
    def _recommend_next_actions(
        self,
        quality_tier: str,
        insights: List[str]
    ) -> List[str]:
        """Recommend next actions based on lead quality."""
        actions = []
        
        if quality_tier == "hot":
            actions.extend([
                "📞 Call or schedule meeting within 24 hours",
                "💰 Send pricing and proposal",
                "🎯 Assign to senior sales rep",
            ])
        elif quality_tier == "warm":
            actions.extend([
                "📧 Send detailed information/case studies",
                "📅 Schedule demo or consultation",
                "👥 Add to nurture sequence",
            ])
        elif quality_tier == "cold":
            actions.extend([
                "📚 Share educational content",
                "❓ Ask qualifying questions",
                "⏰ Follow up in 3-5 days",
            ])
        else:  # inactive
            actions.extend([
                "🔄 Add to re-engagement campaign",
                "🎁 Send special offer or incentive",
                "❌ Consider removing if no response",
            ])
        
        return actions
    
    async def score_batch(
        self,
        leads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Score multiple leads in batch.
        
        Args:
            leads: List of leads to score (each with contact, history, engagement)
            
        Returns:
            List of scoring results
        """
        import asyncio
        
        tasks = [
            self.score_lead(
                lead.get("contact", {}),
                lead.get("conversation_history"),
                lead.get("engagement_data")
            )
            for lead in leads
        ]
        
        return await asyncio.gather(*tasks)
    
    async def identify_hot_leads(
        self,
        leads: List[Dict[str, Any]],
        threshold: int = 80
    ) -> List[Dict[str, Any]]:
        """
        Identify hot leads above score threshold.
        
        Args:
            leads: List of leads to analyze
            threshold: Minimum score for hot lead
            
        Returns:
            List of hot leads with scores
        """
        scored_leads = await self.score_batch(leads)
        
        hot_leads = [
            {**lead, "score": score}
            for lead, score in zip(leads, scored_leads)
            if score["total_score"] >= threshold
        ]
        
        # Sort by score descending
        hot_leads.sort(key=lambda x: x["score"]["total_score"], reverse=True)
        
        return hot_leads
