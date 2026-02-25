"""CRUD operations for Campaign model."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from apps.api.app.models.campaign import Campaign, CampaignStatus, CampaignType


class CampaignCRUD:
    """CRUD operations for Campaign model."""

    def create(self, db: Session, **campaign_data) -> Campaign:
        """Create a new campaign."""
        campaign = Campaign(**campaign_data)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        return campaign

    def get(self, db: Session, campaign_id: int) -> Optional[Campaign]:
        """Get a campaign by ID."""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def get_by_name(self, db: Session, name: str, created_by: Optional[int] = None) -> Optional[Campaign]:
        """Get a campaign by name, optionally filtered by creator."""
        query = db.query(Campaign).filter(Campaign.name == name)
        if created_by:
            query = query.filter(Campaign.created_by == created_by)
        return query.first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        created_by: Optional[int] = None,
        status: Optional[CampaignStatus] = None,
        type: Optional[CampaignType] = None,
        search: Optional[str] = None
    ) -> List[Campaign]:
        """Get multiple campaigns with optional filtering."""
        query = db.query(Campaign)
        
        if created_by:
            query = query.filter(Campaign.created_by == created_by)
            
        if status:
            query = query.filter(Campaign.status == status)
            
        if type:
            query = query.filter(Campaign.type == type)
        
        if search:
            search_filter = or_(
                Campaign.name.ilike(f"%{search}%"),
                Campaign.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, db: Session, campaign: Campaign, **update_data) -> Campaign:
        """Update a campaign."""
        for field, value in update_data.items():
            if hasattr(campaign, field):
                setattr(campaign, field, value)
        
        db.commit()
        db.refresh(campaign)
        return campaign

    def delete(self, db: Session, campaign_id: int) -> bool:
        """Delete a campaign."""
        campaign = self.get(db, campaign_id)
        if campaign:
            db.delete(campaign)
            db.commit()
            return True
        return False

    def get_active_campaigns(self, db: Session) -> List[Campaign]:
        """Get all active (running or scheduled) campaigns."""
        return db.query(Campaign).filter(
            Campaign.status.in_([CampaignStatus.RUNNING, CampaignStatus.SCHEDULED])
        ).all()

    def get_campaigns_by_creator(self, db: Session, user_id: int, limit: int = 100) -> List[Campaign]:
        """Get campaigns created by a specific user."""
        return db.query(Campaign).filter(
            Campaign.created_by == user_id
        ).order_by(Campaign.created_at.desc()).limit(limit).all()

    def get_scheduled_campaigns(self, db: Session, before_time: Optional[datetime] = None) -> List[Campaign]:
        """Get campaigns scheduled to start."""
        query = db.query(Campaign).filter(Campaign.status == CampaignStatus.SCHEDULED)
        
        if before_time:
            query = query.filter(Campaign.scheduled_at <= before_time)
        
        return query.all()

    def start_campaign(self, db: Session, campaign_id: int) -> bool:
        """Start a campaign."""
        campaign = self.get(db, campaign_id)
        if campaign and campaign.status in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
            campaign.start()
            db.commit()
            return True
        return False

    def pause_campaign(self, db: Session, campaign_id: int) -> bool:
        """Pause a campaign."""
        campaign = self.get(db, campaign_id)
        if campaign and campaign.status == CampaignStatus.RUNNING:
            campaign.pause()
            db.commit()
            return True
        return False

    def complete_campaign(self, db: Session, campaign_id: int) -> bool:
        """Mark a campaign as completed."""
        campaign = self.get(db, campaign_id)
        if campaign and campaign.status in [CampaignStatus.RUNNING, CampaignStatus.PAUSED]:
            campaign.complete()
            db.commit()
            return True
        return False

    def cancel_campaign(self, db: Session, campaign_id: int) -> bool:
        """Cancel a campaign."""
        campaign = self.get(db, campaign_id)
        if campaign and campaign.status not in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
            campaign.cancel()
            db.commit()
            return True
        return False

    def update_stats(
        self, 
        db: Session, 
        campaign_id: int,
        messages_sent: Optional[int] = None,
        messages_delivered: Optional[int] = None,
        messages_read: Optional[int] = None,
        replies_received: Optional[int] = None,
        opt_outs: Optional[int] = None
    ) -> bool:
        """Update campaign statistics."""
        campaign = self.get(db, campaign_id)
        if not campaign:
            return False
        
        if messages_sent is not None:
            campaign.messages_sent = messages_sent
        if messages_delivered is not None:
            campaign.messages_delivered = messages_delivered
        if messages_read is not None:
            campaign.messages_read = messages_read
        if replies_received is not None:
            campaign.replies_received = replies_received
        if opt_outs is not None:
            campaign.opt_outs = opt_outs
        
        db.commit()
        return True

    def increment_stats(
        self, 
        db: Session, 
        campaign_id: int,
        messages_sent: int = 0,
        messages_delivered: int = 0,
        messages_read: int = 0,
        replies_received: int = 0,
        opt_outs: int = 0
    ) -> bool:
        """Increment campaign statistics."""
        campaign = self.get(db, campaign_id)
        if not campaign:
            return False
        
        campaign.messages_sent += messages_sent
        campaign.messages_delivered += messages_delivered
        campaign.messages_read += messages_read
        campaign.replies_received += replies_received
        campaign.opt_outs += opt_outs
        
        db.commit()
        return True

    def count(
        self, 
        db: Session, 
        created_by: Optional[int] = None,
        status: Optional[CampaignStatus] = None
    ) -> int:
        """Count campaigns with optional filtering."""
        query = db.query(Campaign)
        
        if created_by:
            query = query.filter(Campaign.created_by == created_by)
            
        if status:
            query = query.filter(Campaign.status == status)
        
        return query.count()


# Global instance
campaign_crud = CampaignCRUD()


# Helper functions for workers
def get_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
    """Get campaign by ID."""
    return campaign_crud.get(db, campaign_id)


def update_campaign(db: Session, campaign_id: int, update_data: dict) -> Optional[Campaign]:
    """Update campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if campaign:
        return campaign_crud.update(db, campaign, **update_data)
    return None


def get_campaigns_by_status(db: Session, status: CampaignStatus) -> List[Campaign]:
    """Get campaigns by status."""
    return db.query(Campaign).filter(Campaign.status == status).all()


def get_campaigns_by_type(db: Session, campaign_type: str) -> List[Campaign]:
    """Get campaigns by type."""
    return db.query(Campaign).filter(Campaign.type == campaign_type).all()


def get_all_campaigns(db: Session, skip: int = 0, limit: int = 1000) -> List[Campaign]:
    """Get all campaigns."""
    return campaign_crud.get_multi(db, skip=skip, limit=limit)