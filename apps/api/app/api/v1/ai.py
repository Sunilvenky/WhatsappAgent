"""
AI feature endpoints for message rewriting, classification, and lead scoring.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ...core.database import get_db
from ...auth.dependencies import get_current_user
from ...models.user import User
from ...ai import MessageRewriter, ReplyClassifier, BanRiskDetector, LeadScorer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Schemas ---

class MessageRewriteRequest(BaseModel):
    """Request to rewrite a message."""
    message: str
    contact_name: Optional[str] = None
    tone: str = "friendly"
    context: Optional[Dict[str, Any]] = None


class MessageRewriteResponse(BaseModel):
    """Response with rewritten message."""
    original: str
    rewritten: str
    tone: str


class MessageAlternativesRequest(BaseModel):
    """Request for message alternatives."""
    message: str
    num_alternatives: int = 3


class ReplyClassificationRequest(BaseModel):
    """Request to classify a reply."""
    reply_text: str
    original_message: Optional[str] = None
    conversation_history: Optional[List[str]] = None


class BanRiskRequest(BaseModel):
    """Request to check ban risk."""
    message: Optional[str] = None
    phone_number_id: Optional[int] = None
    hours: int = 24


class LeadScoreRequest(BaseModel):
    """Request to score a lead."""
    contact_id: int


# --- Message Rewriting Endpoints ---

@router.post("/ai/rewrite", response_model=MessageRewriteResponse)
async def rewrite_message(
    request: MessageRewriteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Rewrite a message to sound more natural and engaging.
    
    Uses AI to transform marketing messages into human-like, engaging text.
    """
    try:
        rewriter = MessageRewriter()
        
        rewritten = await rewriter.rewrite_message(
            original_message=request.message,
            contact_name=request.contact_name,
            tone=request.tone,
            context=request.context
        )
        
        return MessageRewriteResponse(
            original=request.message,
            rewritten=rewritten,
            tone=request.tone
        )
        
    except Exception as e:
        logger.error(f"Message rewriting failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rewrite message: {str(e)}"
        )


@router.post("/ai/alternatives")
async def generate_alternatives(
    request: MessageAlternativesRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate multiple alternative versions of a message."""
    try:
        rewriter = MessageRewriter()
        
        alternatives = await rewriter.suggest_alternatives(
            original_message=request.message,
            num_alternatives=request.num_alternatives
        )
        
        return {
            "original": request.message,
            "alternatives": alternatives,
            "count": len(alternatives)
        }
        
    except Exception as e:
        logger.error(f"Alternative generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate alternatives: {str(e)}"
        )


@router.post("/ai/spam-check")
async def check_spam_risk(
    request: MessageRewriteRequest,
    current_user: User = Depends(get_current_user)
):
    """Check message for spam risk factors."""
    try:
        rewriter = MessageRewriter()
        
        spam_analysis = await rewriter.check_spam_risk(request.message)
        
        return spam_analysis
        
    except Exception as e:
        logger.error(f"Spam check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check spam risk: {str(e)}"
        )


# --- Reply Classification Endpoints ---

@router.post("/ai/classify")
async def classify_reply(
    request: ReplyClassificationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Classify an incoming reply message.
    
    Determines intent, sentiment, and suggests follow-up actions.
    """
    try:
        classifier = ReplyClassifier()
        
        classification = await classifier.classify_reply(
            reply_text=request.reply_text,
            original_message=request.original_message,
            conversation_history=request.conversation_history
        )
        
        # Get auto-response recommendation
        auto_response = await classifier.should_auto_respond(classification)
        
        return {
            **classification,
            "auto_response": auto_response
        }
        
    except Exception as e:
        logger.error(f"Reply classification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify reply: {str(e)}"
        )


# --- Ban Risk Detection Endpoints ---

@router.post("/ai/ban-risk")
async def analyze_ban_risk(
    request: BanRiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze ban risk for a message or phone number's sending pattern.
    """
    try:
        detector = BanRiskDetector()
        
        if request.message:
            # Analyze single message content
            analysis = await detector.analyze_message_content(request.message)
        elif request.phone_number_id:
            # Analyze sending pattern
            from ...crud import message as message_crud
            from datetime import datetime, timedelta
            
            # Get recent messages
            messages = message_crud.get_recent_messages(
                db,
                phone_number_id=request.phone_number_id,
                hours=request.hours
            )
            
            message_data = [
                {
                    "text": msg.content,
                    "sent_at": msg.sent_at,
                    "replied": bool(msg.reply),
                    "blocked": msg.status == "blocked",
                }
                for msg in messages
            ]
            
            analysis = await detector.analyze_message_pattern(
                message_data,
                time_window_hours=request.hours
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either 'message' or 'phone_number_id'"
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ban risk analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze ban risk: {str(e)}"
        )


# --- Lead Scoring Endpoints ---

@router.post("/ai/score-lead")
async def score_lead(
    request: LeadScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Score a lead based on engagement, profile, and behavior.
    """
    try:
        from ...crud import contact as contact_crud
        from ...crud import conversation as conversation_crud
        from ...crud import message as message_crud
        
        # Get contact
        contact = contact_crud.get_contact(db, request.contact_id)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # Get conversation history
        conversation = conversation_crud.get_conversation_by_contact(db, contact.id)
        conversation_history = []
        engagement_data = {}
        
        if conversation:
            messages = message_crud.get_messages_by_conversation(db, conversation.id)
            conversation_history = [
                {
                    "text": msg.content,
                    "from_contact": msg.direction == "inbound",
                    "timestamp": msg.sent_at or msg.received_at
                }
                for msg in messages
            ]
            
            # Calculate engagement metrics
            total_sent = sum(1 for msg in messages if msg.direction == "outbound")
            total_replied = sum(1 for msg in messages if msg.reply_id)
            
            engagement_data = {
                "response_rate": (total_replied / total_sent) if total_sent > 0 else 0,
                "total_messages": len(messages),
                "total_sent": total_sent,
                "total_replied": total_replied,
            }
        
        # Score lead
        scorer = LeadScorer()
        score_result = await scorer.score_lead(
            contact={
                "id": contact.id,
                "name": contact.name,
                "phone": contact.phone,
                "email": contact.email,
                "metadata": contact.metadata or {}
            },
            conversation_history=conversation_history,
            engagement_data=engagement_data
        )
        
        return score_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lead scoring failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score lead: {str(e)}"
        )


@router.get("/ai/hot-leads")
async def get_hot_leads(
    threshold: int = 80,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of hot leads above score threshold."""
    try:
        from ...crud import contact as contact_crud
        
        # Get all contacts (in production, you'd want pagination)
        contacts = contact_crud.get_all_contacts(db, skip=0, limit=limit)
        
        # Build leads data
        leads = []
        for contact in contacts:
            lead_score = contact.metadata.get("lead_score") if contact.metadata else None
            if lead_score and lead_score >= threshold:
                leads.append({
                    "contact_id": contact.id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "email": contact.email,
                    "score": lead_score,
                    "quality": contact.metadata.get("lead_quality"),
                })
        
        # Sort by score descending
        leads.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "hot_leads": leads,
            "count": len(leads),
            "threshold": threshold
        }
        
    except Exception as e:
        logger.error(f"Failed to get hot leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hot leads: {str(e)}"
        )
