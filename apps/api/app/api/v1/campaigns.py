"""Campaign management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.crud import campaign as campaign_crud
from apps.api.app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignSearchParams,
    CampaignStats
)
from apps.api.app.models.campaign import CampaignStatus, CampaignType
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign."""
    try:
        campaign_data = campaign.model_dump()
        campaign_data["created_by"] = current_user.id
        
        db_campaign = campaign_crud.create(db, **campaign_data)
        return db_campaign
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[CampaignStatus] = Query(None),
    type: Optional[CampaignType] = Query(None),
    created_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List campaigns with optional filtering."""
    search_params = CampaignSearchParams(
        search=search,
        status=status,
        type=type,
        created_by=created_by,
        skip=skip,
        limit=limit
    )
    
    campaigns = campaign_crud.search_campaigns(db, search_params)
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific campaign by ID."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can update this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this campaign"
        )
    
    # Prevent updating running or completed campaigns
    if campaign.status in [CampaignStatus.RUNNING, CampaignStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update campaign in {campaign.status.value} status"
        )
    
    updated_campaign = campaign_crud.update(
        db, 
        campaign, 
        **campaign_update.model_dump(exclude_unset=True)
    )
    return updated_campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can delete this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this campaign"
        )
    
    # Prevent deleting running campaigns
    if campaign.status == CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a running campaign. Stop it first."
        )
    
    campaign_crud.delete(db, campaign_id)


@router.post("/{campaign_id}/start", response_model=CampaignResponse)
def start_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can start this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start this campaign"
        )
    
    # Validate campaign can be started
    if campaign.status != CampaignStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campaign in {campaign.status.value} status cannot be started"
        )
    
    success = campaign_crud.start_campaign(db, campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to start campaign. Check campaign configuration."
        )
    
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
def pause_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pause a running campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can pause this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pause this campaign"
        )
    
    if campaign.status != CampaignStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only running campaigns can be paused"
        )
    
    success = campaign_crud.pause_campaign(db, campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to pause campaign"
        )
    
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/resume", response_model=CampaignResponse)
def resume_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume a paused campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can resume this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to resume this campaign"
        )
    
    if campaign.status != CampaignStatus.PAUSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paused campaigns can be resumed"
        )
    
    success = campaign_crud.resume_campaign(db, campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to resume campaign"
        )
    
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/stop", response_model=CampaignResponse)
def stop_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop a campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can stop this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to stop this campaign"
        )
    
    if campaign.status not in [CampaignStatus.RUNNING, CampaignStatus.PAUSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only running or paused campaigns can be stopped"
        )
    
    success = campaign_crud.stop_campaign(db, campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to stop campaign"
        )
    
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/complete", response_model=CampaignResponse)
def complete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a campaign as completed."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if user can complete this campaign
    if campaign.created_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this campaign"
        )
    
    success = campaign_crud.complete_campaign(db, campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to complete campaign"
        )
    
    db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}/stats", response_model=CampaignStats)
def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign statistics."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignStats(
        messages_sent=campaign.messages_sent,
        messages_delivered=campaign.messages_delivered,
        messages_read=campaign.messages_read,
        replies_received=campaign.replies_received,
        delivery_rate=campaign.delivery_rate,
        open_rate=campaign.open_rate,
        reply_rate=campaign.reply_rate,
        leads_generated=campaign.leads_generated,
        conversion_rate=campaign.conversion_rate
    )


@router.put("/{campaign_id}/stats")
def update_campaign_stats(
    campaign_id: int,
    messages_sent: Optional[int] = Query(None),
    messages_delivered: Optional[int] = Query(None),
    messages_read: Optional[int] = Query(None),
    replies_received: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update campaign statistics."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    success = campaign_crud.update_stats(
        db,
        campaign_id,
        messages_sent=messages_sent,
        messages_delivered=messages_delivered,
        messages_read=messages_read,
        replies_received=replies_received
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update campaign statistics"
        )
    
    return {"message": "Campaign statistics updated successfully"}


@router.get("/stats/overview")
def get_campaign_overview(
    created_by: Optional[int] = Query(None),
    status: Optional[CampaignStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get campaign overview statistics."""
    # If not admin, only show user's own campaigns
    if current_user.role.value != "admin" and not created_by:
        created_by = current_user.id
    
    search_params = CampaignSearchParams(
        status=status,
        created_by=created_by,
        skip=0,
        limit=1000  # Get all for stats
    )
    
    campaigns = campaign_crud.search_campaigns(db, search_params)
    
    # Calculate overview statistics
    total_campaigns = len(campaigns)
    draft_campaigns = len([c for c in campaigns if c.status == CampaignStatus.DRAFT])
    running_campaigns = len([c for c in campaigns if c.status == CampaignStatus.RUNNING])
    completed_campaigns = len([c for c in campaigns if c.status == CampaignStatus.COMPLETED])
    
    total_sent = sum(c.messages_sent for c in campaigns)
    total_delivered = sum(c.messages_delivered for c in campaigns)
    total_read = sum(c.messages_read for c in campaigns)
    total_replies = sum(c.replies_received for c in campaigns)
    
    # Calculate overall rates
    overall_delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
    overall_open_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0
    overall_reply_rate = (total_replies / total_read * 100) if total_read > 0 else 0
    
    return {
        "total_campaigns": total_campaigns,
        "draft_campaigns": draft_campaigns,
        "running_campaigns": running_campaigns,
        "completed_campaigns": completed_campaigns,
        "total_messages_sent": total_sent,
        "total_messages_delivered": total_delivered,
        "total_messages_read": total_read,
        "total_replies": total_replies,
        "overall_delivery_rate": round(overall_delivery_rate, 2),
        "overall_open_rate": round(overall_open_rate, 2),
        "overall_reply_rate": round(overall_reply_rate, 2)
    }


@router.post("/{campaign_id}/duplicate", response_model=CampaignResponse)
def duplicate_campaign(
    campaign_id: int,
    new_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate an existing campaign."""
    campaign = campaign_crud.get(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Create duplicate
    duplicate_name = new_name or f"{campaign.name} (Copy)"
    
    duplicate_data = {
        "name": duplicate_name,
        "description": campaign.description,
        "type": campaign.type,
        "message_template": campaign.message_template,
        "target_criteria": campaign.target_criteria,
        "personalization_fields": campaign.personalization_fields,
        "created_by": current_user.id
    }
    
    duplicate_campaign = campaign_crud.create(db, **duplicate_data)
    return duplicate_campaign