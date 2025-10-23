"""Pydantic schemas for Lead model."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from apps.api.app.models.lead import LeadStatus, LeadSource, LeadPriority


# Lead schemas
class LeadBase(BaseModel):
    """Base schema for Lead."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: LeadPriority = LeadPriority.MEDIUM
    source: LeadSource = LeadSource.WHATSAPP_CAMPAIGN
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=3)
    probability: int = Field(default=10, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    lead_score: int = Field(default=0, ge=0, le=100)
    qualification_notes: Optional[str] = None
    pain_points: Optional[List[str]] = None
    budget_range: Optional[str] = Field(None, max_length=100)
    decision_maker: bool = False
    conversion_source: Optional[str] = Field(None, max_length=100)
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    tags: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead."""
    contact_id: int
    campaign_id: Optional[int] = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    source: Optional[LeadSource] = None
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    lead_score: Optional[int] = Field(None, ge=0, le=100)
    qualification_notes: Optional[str] = None
    pain_points: Optional[List[str]] = None
    budget_range: Optional[str] = Field(None, max_length=100)
    decision_maker: Optional[bool] = None
    conversion_source: Optional[str] = Field(None, max_length=100)
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    tags: Optional[str] = None
    assigned_to: Optional[int] = None


class Lead(LeadBase):
    """Schema for Lead response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contact_id: int
    assigned_to: Optional[int] = None
    campaign_id: Optional[int] = None
    status: LeadStatus
    actual_close_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_open: bool
    is_won: bool
    is_lost: bool
    is_hot: bool
    expected_revenue: float
    days_since_created: int
    is_overdue: bool


# Lead action schemas
class LeadAction(BaseModel):
    """Schema for lead actions."""
    action: str = Field(..., pattern="^(close_won|close_lost|assign|contact|qualify)$")
    value: Optional[Decimal] = Field(None, ge=0)  # For close_won
    reason: Optional[str] = None  # For close_lost
    user_id: Optional[int] = None  # For assign


class LeadAssignment(BaseModel):
    """Schema for assigning a lead to a user."""
    assigned_to: int


class LeadScoreUpdate(BaseModel):
    """Schema for updating lead score."""
    lead_score: int = Field(..., ge=0, le=100)
    notes: Optional[str] = None


class LeadFollowUp(BaseModel):
    """Schema for scheduling lead follow-up."""
    follow_up_date: datetime
    notes: Optional[str] = None


# Lead search and filter schemas
class LeadSearch(BaseModel):
    """Schema for lead search parameters."""
    assigned_to: Optional[int] = None
    status: Optional[LeadStatus] = None
    priority: Optional[LeadPriority] = None
    source: Optional[LeadSource] = None
    search: Optional[str] = None
    min_score: Optional[int] = Field(None, ge=0, le=100)
    max_score: Optional[int] = Field(None, ge=0, le=100)
    min_value: Optional[Decimal] = Field(None, ge=0)
    max_value: Optional[Decimal] = Field(None, ge=0)
    expected_close_before: Optional[datetime] = None
    expected_close_after: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


# Lead with related data
class LeadWithContact(Lead):
    """Lead schema with contact information."""
    contact: Optional[Dict[str, Any]] = None


class LeadWithCampaign(Lead):
    """Lead schema with campaign information."""
    campaign: Optional[Dict[str, Any]] = None


class LeadFull(Lead):
    """Complete lead schema with all related data."""
    contact: Optional[Dict[str, Any]] = None
    assigned_user: Optional[Dict[str, Any]] = None
    campaign: Optional[Dict[str, Any]] = None


# Lead statistics schemas
class LeadStats(BaseModel):
    """Schema for lead statistics."""
    total: int
    open: int
    won: int
    lost: int
    hot: int
    overdue: int
    total_value: Decimal
    expected_revenue: Decimal
    won_value: Decimal
    conversion_rate: float
    average_deal_size: Decimal
    average_sales_cycle: Optional[float] = None  # in days


class UserLeadStats(BaseModel):
    """Schema for user-specific lead statistics."""
    user_id: int
    assigned_leads: int
    open_leads: int
    won_leads: int
    lost_leads: int
    hot_leads: int
    overdue_leads: int
    total_value: Decimal
    won_value: Decimal
    conversion_rate: float


class LeadPerformance(BaseModel):
    """Schema for lead performance metrics."""
    period: str  # daily, weekly, monthly
    date: datetime
    new_leads: int
    qualified_leads: int
    closed_won: int
    closed_lost: int
    total_value_won: Decimal
    conversion_rate: float
    average_deal_size: Decimal


# Lead pipeline schemas
class LeadPipeline(BaseModel):
    """Schema for lead pipeline view."""
    status: LeadStatus
    count: int
    total_value: Decimal
    expected_revenue: Decimal
    leads: List[Lead] = []


class SalesFunnel(BaseModel):
    """Schema for sales funnel metrics."""
    new: int
    contacted: int
    qualified: int
    proposal: int
    negotiation: int
    closed_won: int
    closed_lost: int
    conversion_rates: Dict[str, float]


# Aliases for backwards compatibility
LeadResponse = Lead
LeadSearchParams = LeadSearch