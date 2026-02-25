"""Lead management API endpoints."""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.crud import lead_crud
from apps.api.app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadResponse,
    LeadSearchParams,
    LeadStats
)
from apps.api.app.models.lead import LeadStatus, LeadPriority, LeadSource
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User

router = APIRouter()


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lead."""
    try:
        lead_data = lead.model_dump()
        
        # Auto-assign to current user if not specified and user is sales
        if not lead_data.get("assigned_to") and current_user.role.value in ["sales", "marketer"]:
            lead_data["assigned_to"] = current_user.id
        
        db_lead = lead_crud.create(db, **lead_data)
        return db_lead
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create lead: {str(e)}"
        )


@router.get("/", response_model=List[LeadResponse])
def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[LeadStatus] = Query(None),
    priority: Optional[LeadPriority] = Query(None),
    source: Optional[LeadSource] = Query(None),
    assigned_to: Optional[int] = Query(None),
    campaign_id: Optional[int] = Query(None),
    min_value: Optional[float] = Query(None),
    max_value: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List leads with optional filtering."""
    # If not admin and no assigned_to specified, show user's assigned leads
    if current_user.role.value not in ["admin", "marketer"] and assigned_to is None:
        assigned_to = current_user.id
    
    search_params = LeadSearchParams(
        search=search,
        status=status,
        priority=priority,
        source=source,
        assigned_to=assigned_to,
        campaign_id=campaign_id,
        min_value=Decimal(str(min_value)) if min_value is not None else None,
        max_value=Decimal(str(max_value)) if max_value is not None else None,
        skip=skip,
        limit=limit
    )
    
    leads = lead_crud.get_multi(
        db, 
        **search_params.model_dump()
    )
    return leads


@router.get("/assigned", response_model=List[LeadResponse])
def get_assigned_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[LeadStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leads assigned to the current user."""
    leads = lead_crud.get_assigned_leads(
        db, 
        current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )
    return leads


@router.get("/high-priority", response_model=List[LeadResponse])
def get_high_priority_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get high priority leads."""
    # If not admin and no assigned_to specified, show user's high priority leads
    if current_user.role.value not in ["admin", "marketer"] and assigned_to is None:
        assigned_to = current_user.id
    
    leads = lead_crud.get_high_priority_leads(
        db, 
        assigned_to=assigned_to,
        skip=skip,
        limit=limit
    )
    return leads


@router.get("/overdue", response_model=List[LeadResponse])
def get_overdue_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overdue leads (past follow-up date)."""
    # If not admin and no assigned_to specified, show user's overdue leads
    if current_user.role.value not in ["admin", "marketer"] and assigned_to is None:
        assigned_to = current_user.id
    
    leads = lead_crud.get_overdue_leads(
        db, 
        assigned_to=assigned_to,
        skip=skip,
        limit=limit
    )
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific lead by ID."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check access permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this lead"
        )
    
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a lead."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check update permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lead"
        )
    
    updated_lead = lead_crud.update(
        db, 
        lead, 
        **lead_update.model_dump(exclude_unset=True)
    )
    return updated_lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a lead."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check delete permissions (admin or marketer only)
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete leads"
        )
    
    lead_crud.delete(db, lead_id)


@router.post("/{lead_id}/assign", response_model=LeadResponse)
def assign_lead(
    lead_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a lead to a user."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check assignment permissions
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign leads"
        )
    
    success = lead_crud.assign_lead(db, lead_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign lead"
        )
    
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/contacted", response_model=LeadResponse)
def mark_contacted(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a lead as contacted."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lead"
        )
    
    success = lead_crud.mark_contacted(db, lead_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to mark lead as contacted"
        )
    
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/follow-up", response_model=LeadResponse)
def schedule_follow_up(
    lead_id: int,
    follow_up_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule a follow-up for a lead."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lead"
        )
    
    success = lead_crud.schedule_follow_up(db, lead_id, follow_up_date)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to schedule follow-up"
        )
    
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/score", response_model=LeadResponse)
def update_lead_score(
    lead_id: int,
    score: int = Query(..., ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update lead score."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lead"
        )
    
    success = lead_crud.update_score(db, lead_id, score)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update lead score"
        )
    
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/convert", response_model=LeadResponse)
def convert_lead(
    lead_id: int,
    conversion_value: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Convert a lead (mark as won)."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to convert this lead"
        )
    
    # Use provided value or estimated value
    final_value = Decimal(str(conversion_value)) if conversion_value else lead.estimated_value
    
    success = lead_crud.close_won(db, lead_id, final_value)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to convert lead"
        )
    
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/close-lost", response_model=LeadResponse)
def close_lead_lost(
    lead_id: int,
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close a lead as lost."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this lead"
        )
    
    success = lead_crud.close_lost(db, lead_id, reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to close lead as lost"
        )
    
    db.refresh(lead)
    return lead


@router.get("/{lead_id}/activities")
def get_lead_activities(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead activity history."""
    lead = lead_crud.get(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Check permissions
    if (lead.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this lead"
        )
    
    activities = lead_crud.get_lead_activities(db, lead_id)
    return activities


@router.get("/stats/overview", response_model=LeadStats)
def get_lead_stats(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead statistics overview."""
    # If not admin and no user_id specified, show current user's stats
    if current_user.role.value not in ["admin", "marketer"] and user_id is None:
        user_id = current_user.id
    
    stats = lead_crud.get_lead_stats(db, user_id=user_id)
    return LeadStats(**stats)


@router.get("/stats/pipeline")
def get_pipeline_stats(
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sales pipeline statistics."""
    # If not admin and no assigned_to specified, show user's pipeline
    if current_user.role.value not in ["admin", "marketer"] and assigned_to is None:
        assigned_to = current_user.id
    
    # Get leads by status
    leads = lead_crud.get_multi(db, assigned_to=assigned_to, limit=1000)
    
    # Calculate pipeline statistics
    pipeline_stats = {}
    total_value = Decimal('0.00')
    weighted_value = Decimal('0.00')
    
    for status in LeadStatus:
        status_leads = [l for l in leads if l.status == status]
        status_count = len(status_leads)
        status_value = sum(l.estimated_value or Decimal('0.00') for l in status_leads)
        
        pipeline_stats[status.value] = {
            "count": status_count,
            "value": float(status_value)
        }
        
        if status != LeadStatus.CLOSED_LOST:
            total_value += status_value
            # Calculate weighted value based on probability
            for lead in status_leads:
                weighted_value += (lead.estimated_value or Decimal('0.00')) * Decimal(str(lead.probability / 100))
    
    pipeline_stats["total_value"] = float(total_value)
    pipeline_stats["weighted_value"] = float(weighted_value)
    pipeline_stats["total_leads"] = len(leads)
    
    return pipeline_stats


@router.get("/stats/conversion-funnel")
def get_conversion_funnel(
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead conversion funnel statistics."""
    # If not admin and no assigned_to specified, show user's funnel
    if current_user.role.value not in ["admin", "marketer"] and assigned_to is None:
        assigned_to = current_user.id
    
    leads = lead_crud.get_multi(db, assigned_to=assigned_to, limit=1000)
    
    # Define funnel stages in order
    funnel_stages = [
        LeadStatus.NEW,
        LeadStatus.CONTACTED,
        LeadStatus.QUALIFIED,
        LeadStatus.PROPOSAL,
        LeadStatus.NEGOTIATION,
        LeadStatus.CLOSED_WON
    ]
    
    funnel_data = []
    total_leads = len(leads)
    
    for stage in funnel_stages:
        stage_leads = [l for l in leads if l.status == stage]
        stage_count = len(stage_leads)
        conversion_rate = (stage_count / total_leads * 100) if total_leads > 0 else 0
        
        funnel_data.append({
            "stage": stage.value,
            "count": stage_count,
            "conversion_rate": round(conversion_rate, 2)
        })
    
    return {
        "funnel": funnel_data,
        "total_leads": total_leads
    }


@router.post("/bulk/assign")
def bulk_assign_leads(
    lead_ids: List[int],
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk assign leads to a user."""
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign leads"
        )
    
    success_count = 0
    failed_count = 0
    
    for lead_id in lead_ids:
        try:
            success = lead_crud.assign_lead(db, lead_id, user_id)
            if success:
                success_count += 1
            else:
                failed_count += 1
        except:
            failed_count += 1
    
    return {
        "assigned": success_count,
        "failed": failed_count,
        "total": len(lead_ids)
    }


@router.post("/bulk/update-status")
def bulk_update_status(
    lead_ids: List[int],
    status: LeadStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk update lead status."""
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to bulk update leads"
        )
    
    success_count = 0
    failed_count = 0
    
    for lead_id in lead_ids:
        try:
            lead = lead_crud.get(db, lead_id)
            if lead:
                lead_crud.update(db, lead, status=status)
                success_count += 1
            else:
                failed_count += 1
        except:
            failed_count += 1
    
    return {
        "updated": success_count,
        "failed": failed_count,
        "total": len(lead_ids)
    }