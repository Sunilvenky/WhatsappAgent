"""
Analytics and reporting endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ...core.database import get_db
from ...auth.dependencies import get_current_user
from ...models.user import User
from ...models.message import Message, MessageStatus
from ...models.campaign import Campaign, CampaignStatus
from ...models.conversation import Conversation
from ...workers.analytics_worker import calculate_campaign_analytics
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Schemas ---

class CampaignAnalytics(BaseModel):
    """Campaign analytics response."""
    campaign_id: int
    campaign_name: str
    status: str
    analytics: Dict[str, Any]


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_messages_sent: int
    total_messages_received: int
    total_contacts: int
    total_campaigns: int
    active_campaigns: int
    avg_response_rate: float
    today_messages: int
    this_week_messages: int


# --- Analytics Endpoints ---

@router.get("/analytics/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall dashboard statistics.
    """
    try:
        from ...crud import contact as contact_crud
        from ...crud import campaign as campaign_crud
        
        # Total messages
        total_sent = db.query(func.count(Message.id)).filter(
            Message.direction == "outbound"
        ).scalar() or 0
        
        total_received = db.query(func.count(Message.id)).filter(
            Message.direction == "inbound"
        ).scalar() or 0
        
        # Total contacts
        total_contacts = db.query(func.count).select_from(
            contact_crud.Contact
        ).scalar() or 0
        
        # Campaigns
        total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0
        active_campaigns = db.query(func.count(Campaign.id)).filter(
            Campaign.status == CampaignStatus.RUNNING
        ).scalar() or 0
        
        # Response rate
        replied_count = db.query(func.count(Message.id)).filter(
            Message.reply_id.isnot(None)
        ).scalar() or 0
        avg_response_rate = (replied_count / total_sent * 100) if total_sent > 0 else 0
        
        # Today's messages
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_messages = db.query(func.count(Message.id)).filter(
            Message.sent_at >= today_start
        ).scalar() or 0
        
        # This week's messages
        week_start = today_start - timedelta(days=today_start.weekday())
        week_messages = db.query(func.count(Message.id)).filter(
            Message.sent_at >= week_start
        ).scalar() or 0
        
        return DashboardStats(
            total_messages_sent=total_sent,
            total_messages_received=total_received,
            total_contacts=total_contacts,
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            avg_response_rate=round(avg_response_rate, 2),
            today_messages=today_messages,
            this_week_messages=week_messages
        )
        
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard statistics: {str(e)}"
        )


@router.get("/analytics/campaigns/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed analytics for a specific campaign.
    """
    try:
        from ...crud import campaign as campaign_crud
        
        campaign = campaign_crud.get_campaign(db, campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Calculate analytics
        analytics = calculate_campaign_analytics(db, campaign_id)
        
        return {
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "status": campaign.status,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            "started_at": campaign.started_at.isoformat() if campaign.started_at else None,
            "completed_at": campaign.completed_at.isoformat() if campaign.completed_at else None,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get campaign analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign analytics: {str(e)}"
        )


@router.get("/analytics/campaigns")
async def get_all_campaigns_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for all campaigns."""
    try:
        from ...crud import campaign as campaign_crud
        
        campaigns = campaign_crud.get_all_campaigns(db)
        
        results = []
        for campaign in campaigns:
            analytics = campaign.metadata.get("analytics") if campaign.metadata else None
            
            if not analytics:
                # Calculate if not cached
                analytics = calculate_campaign_analytics(db, campaign.id)
            
            results.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "status": campaign.status,
                "analytics": analytics
            })
        
        return {
            "campaigns": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to get campaigns analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaigns analytics: {str(e)}"
        )


@router.get("/analytics/messages/timeline")
async def get_messages_timeline(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get message volume timeline (sent/received per day).
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query messages by day
        timeline = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            sent_count = db.query(func.count(Message.id)).filter(
                Message.sent_at >= day_start,
                Message.sent_at < day_end,
                Message.direction == "outbound"
            ).scalar() or 0
            
            received_count = db.query(func.count(Message.id)).filter(
                Message.received_at >= day_start,
                Message.received_at < day_end,
                Message.direction == "inbound"
            ).scalar() or 0
            
            timeline.append({
                "date": day.strftime("%Y-%m-%d"),
                "sent": sent_count,
                "received": received_count
            })
        
        return {
            "timeline": timeline,
            "days": days,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        logger.error(f"Failed to get messages timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages timeline: {str(e)}"
        )


@router.get("/analytics/engagement")
async def get_engagement_metrics(
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement metrics (response rates, read rates, etc.)."""
    try:
        # Build query
        query = db.query(Message)
        if campaign_id:
            query = query.filter(Message.campaign_id == campaign_id)
        
        # Total messages
        total = query.count()
        
        # Status breakdown
        delivered = query.filter(Message.status == MessageStatus.DELIVERED).count()
        read = query.filter(Message.status == MessageStatus.READ).count()
        failed = query.filter(Message.status == MessageStatus.FAILED).count()
        replied = query.filter(Message.reply_id.isnot(None)).count()
        
        # Calculate rates
        delivery_rate = (delivered / total * 100) if total > 0 else 0
        read_rate = (read / total * 100) if total > 0 else 0
        response_rate = (replied / total * 100) if total > 0 else 0
        failure_rate = (failed / total * 100) if total > 0 else 0
        
        return {
            "total_messages": total,
            "delivered": delivered,
            "read": read,
            "replied": replied,
            "failed": failed,
            "delivery_rate": round(delivery_rate, 2),
            "read_rate": round(read_rate, 2),
            "response_rate": round(response_rate, 2),
            "failure_rate": round(failure_rate, 2),
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        logger.error(f"Failed to get engagement metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get engagement metrics: {str(e)}"
        )


@router.get("/analytics/top-performers")
async def get_top_performing_contacts(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top performing contacts by lead score and engagement."""
    try:
        from ...crud import contact as contact_crud
        
        contacts = contact_crud.get_all_contacts(db, skip=0, limit=1000)
        
        # Extract lead scores
        scored_contacts = []
        for contact in contacts:
            lead_score = contact.metadata.get("lead_score") if contact.metadata else None
            if lead_score:
                scored_contacts.append({
                    "contact_id": contact.id,
                    "name": contact.name,
                    "phone": contact.phone,
                    "email": contact.email,
                    "lead_score": lead_score,
                    "lead_quality": contact.metadata.get("lead_quality"),
                })
        
        # Sort by score and take top N
        scored_contacts.sort(key=lambda x: x["lead_score"], reverse=True)
        top_performers = scored_contacts[:limit]
        
        return {
            "top_performers": top_performers,
            "count": len(top_performers)
        }
        
    except Exception as e:
        logger.error(f"Failed to get top performers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top performers: {str(e)}"
        )
