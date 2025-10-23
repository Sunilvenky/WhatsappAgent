"""
Analytics and reporting workers.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from .celery_app import celery_app
from ..core.database import get_db
from ..models.message import Message, MessageStatus
from ..models.campaign import Campaign
from ..models.conversation import Conversation

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.analytics_worker.update_campaign_analytics")
def update_campaign_analytics():
    """Update analytics for all active campaigns."""
    db = next(get_db())
    
    try:
        from ..crud import campaign as campaign_crud
        
        campaigns = campaign_crud.get_all_campaigns(db)
        
        for campaign in campaigns:
            analytics = calculate_campaign_analytics(db, campaign.id)
            
            # Update campaign metadata with analytics
            campaign_crud.update_campaign(
                db,
                campaign.id,
                {
                    "metadata": {
                        **campaign.metadata,
                        "analytics": analytics,
                        "last_analytics_update": datetime.utcnow().isoformat()
                    }
                }
            )
        
        logger.info(f"Updated analytics for {len(campaigns)} campaigns")
    
    except Exception as e:
        logger.error(f"Error updating campaign analytics: {e}")
    finally:
        db.close()


def calculate_campaign_analytics(db: Session, campaign_id: int) -> Dict[str, Any]:
    """
    Calculate comprehensive analytics for a campaign.
    
    Args:
        db: Database session
        campaign_id: Campaign ID
        
    Returns:
        Analytics dictionary
    """
    # Message statistics
    message_stats = db.query(
        Message.status,
        func.count(Message.id).label("count")
    ).filter(
        Message.campaign_id == campaign_id
    ).group_by(Message.status).all()
    
    total_sent = sum(stat.count for stat in message_stats)
    status_breakdown = {stat.status: stat.count for stat in message_stats}
    
    # Response statistics
    replied_count = db.query(func.count(Message.id)).filter(
        Message.campaign_id == campaign_id,
        Message.reply_id.isnot(None)
    ).scalar() or 0
    
    response_rate = (replied_count / total_sent * 100) if total_sent > 0 else 0
    
    # Delivery statistics
    delivered_count = status_breakdown.get(MessageStatus.DELIVERED, 0)
    read_count = status_breakdown.get(MessageStatus.READ, 0)
    failed_count = status_breakdown.get(MessageStatus.FAILED, 0)
    
    delivery_rate = (delivered_count / total_sent * 100) if total_sent > 0 else 0
    read_rate = (read_count / total_sent * 100) if total_sent > 0 else 0
    failure_rate = (failed_count / total_sent * 100) if total_sent > 0 else 0
    
    # Time-based analytics
    avg_response_time = db.query(
        func.avg(
            func.extract('epoch', Message.received_at - Message.sent_at)
        )
    ).filter(
        Message.campaign_id == campaign_id,
        Message.reply_id.isnot(None),
        Message.received_at.isnot(None),
        Message.sent_at.isnot(None)
    ).scalar() or 0
    
    # Engagement score (0-100)
    engagement_score = (
        response_rate * 0.5 +
        read_rate * 0.3 +
        delivery_rate * 0.2
    )
    
    return {
        "total_messages": total_sent,
        "status_breakdown": status_breakdown,
        "delivered_count": delivered_count,
        "read_count": read_count,
        "failed_count": failed_count,
        "replied_count": replied_count,
        "response_rate": round(response_rate, 2),
        "delivery_rate": round(delivery_rate, 2),
        "read_rate": round(read_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "avg_response_time_seconds": round(avg_response_time, 2),
        "engagement_score": round(engagement_score, 2),
        "calculated_at": datetime.utcnow().isoformat()
    }


@celery_app.task(name="app.workers.analytics_worker.generate_daily_report")
def generate_daily_report():
    """Generate daily analytics report."""
    db = next(get_db())
    
    try:
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        start_of_day = datetime.combine(yesterday, datetime.min.time())
        end_of_day = datetime.combine(yesterday, datetime.max.time())
        
        # Messages sent yesterday
        messages_sent = db.query(func.count(Message.id)).filter(
            Message.sent_at >= start_of_day,
            Message.sent_at <= end_of_day
        ).scalar() or 0
        
        # Messages received yesterday
        messages_received = db.query(func.count(Message.id)).filter(
            Message.received_at >= start_of_day,
            Message.received_at <= end_of_day,
            Message.direction == "inbound"
        ).scalar() or 0
        
        # Active conversations
        active_conversations = db.query(func.count(Conversation.id)).filter(
            Conversation.last_message_at >= start_of_day,
            Conversation.last_message_at <= end_of_day
        ).scalar() or 0
        
        # Campaign statistics
        campaigns_run = db.query(func.count(Campaign.id)).filter(
            Campaign.started_at >= start_of_day,
            Campaign.started_at <= end_of_day
        ).scalar() or 0
        
        report = {
            "date": yesterday.isoformat(),
            "messages_sent": messages_sent,
            "messages_received": messages_received,
            "active_conversations": active_conversations,
            "campaigns_run": campaigns_run,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Daily report generated: {report}")
        
        # TODO: Send report via email or store in database
        
        return report
    
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return None
    finally:
        db.close()


@celery_app.task(name="app.workers.analytics_worker.update_lead_scores")
def update_lead_scores():
    """Update lead scores for all contacts."""
    db = next(get_db())
    
    try:
        import asyncio
        from ..crud import contact as contact_crud
        from ..ai import LeadScorer
        
        scorer = LeadScorer()
        contacts = contact_crud.get_all_contacts(db)
        
        logger.info(f"Updating lead scores for {len(contacts)} contacts")
        
        async def score_contacts():
            for contact in contacts:
                try:
                    # Get conversation and engagement data
                    from ..crud import conversation as conversation_crud
                    from ..crud import message as message_crud
                    
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
                    
                    # Update contact with lead score
                    contact_crud.update_contact(
                        db,
                        contact.id,
                        {
                            "metadata": {
                                **(contact.metadata or {}),
                                "lead_score": score_result["total_score"],
                                "lead_quality": score_result["quality_tier"],
                                "lead_score_updated_at": datetime.utcnow().isoformat()
                            }
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error scoring contact {contact.id}: {e}")
        
        asyncio.run(score_contacts())
        
        logger.info("Lead scores updated successfully")
    
    except Exception as e:
        logger.error(f"Error updating lead scores: {e}")
    finally:
        db.close()
