"""Pydantic schemas for Campaign model."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from apps.api.app.models.campaign import CampaignStatus, CampaignType


# Campaign schemas
class CampaignBase(BaseModel):
    """Base schema for Campaign."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: CampaignType = CampaignType.BROADCAST
    message_template: str = Field(..., min_length=1)
    target_criteria: Optional[Dict[str, Any]] = None
    personalization_fields: Optional[Dict[str, Any]] = None
    send_immediately: bool = False
    respect_time_zones: bool = True
    send_time_start: Optional[str] = Field(default="09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    send_time_end: Optional[str] = Field(default="18:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign."""
    scheduled_at: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type: Optional[CampaignType] = None
    status: Optional[CampaignStatus] = None
    message_template: Optional[str] = Field(None, min_length=1)
    target_criteria: Optional[Dict[str, Any]] = None
    personalization_fields: Optional[Dict[str, Any]] = None
    send_immediately: Optional[bool] = None
    respect_time_zones: Optional[bool] = None
    send_time_start: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    send_time_end: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    scheduled_at: Optional[datetime] = None


class Campaign(CampaignBase):
    """Schema for Campaign response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: CampaignStatus
    created_by: int
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    total_recipients: int
    messages_sent: int
    messages_delivered: int
    messages_read: int
    replies_received: int
    opt_outs: int
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_active: bool
    delivery_rate: float
    open_rate: float
    reply_rate: float


# Campaign action schemas
class CampaignAction(BaseModel):
    """Schema for campaign actions (start, pause, stop, etc.)."""
    action: str = Field(..., pattern="^(start|pause|resume|complete|cancel)$")


class CampaignSchedule(BaseModel):
    """Schema for scheduling a campaign."""
    scheduled_at: datetime


# Campaign analytics schemas
class CampaignStats(BaseModel):
    """Schema for campaign statistics."""
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    total_messages_sent: int
    total_messages_delivered: int
    total_replies: int
    average_delivery_rate: float
    average_open_rate: float
    average_reply_rate: float


class CampaignPerformance(BaseModel):
    """Schema for detailed campaign performance."""
    campaign_id: int
    campaign_name: str
    status: CampaignStatus
    type: CampaignType
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    total_recipients: int
    messages_sent: int
    messages_delivered: int
    messages_read: int
    replies_received: int
    opt_outs: int
    delivery_rate: float
    open_rate: float
    reply_rate: float
    opt_out_rate: float


# Campaign search and filter schemas
class CampaignSearch(BaseModel):
    """Schema for campaign search parameters."""
    search: Optional[str] = None
    status: Optional[CampaignStatus] = None
    type: Optional[CampaignType] = None
    created_by: Optional[int] = None
    skip: int = 0
    limit: int = 100


# Campaign targeting schemas
class CampaignTargeting(BaseModel):
    """Schema for campaign targeting criteria."""
    include_tags: Optional[List[str]] = None
    exclude_tags: Optional[List[str]] = None
    companies: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    opt_in_status: bool = True
    has_whatsapp: bool = True
    last_contacted_before: Optional[datetime] = None
    last_contacted_after: Optional[datetime] = None


# Campaign preview schemas
class CampaignPreview(BaseModel):
    """Schema for campaign preview."""
    estimated_recipients: int
    sample_contacts: List[Dict[str, Any]]
    personalized_message_samples: List[str]


# Aliases for backwards compatibility
CampaignResponse = Campaign
CampaignSearchParams = CampaignSearch