"""
Drip campaign steps and progress models.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.api.app.core.database import Base


class CampaignStep(Base):
    """Individual steps in a drip campaign."""
    __tablename__ = "campaign_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Step details
    step_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    
    # Timing
    delay_hours = Column(Integer, default=24, nullable=False)  # Delay from previous step or campaign start
    delay_type = Column(String(50), default="hours", nullable=False)  # hours, days, weeks
    
    # Message content
    message_template = Column(String(2000), nullable=False)
    template_variables = Column(JSON, default={}, nullable=False)
    
    # Conditions (optional - can skip step based on conditions)
    conditions = Column(JSON, nullable=True)  # e.g., {"require_previous_engagement": true}
    
    # Fallback for step failure
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Ordering
    order_index = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="campaign_steps")
    campaign = relationship("Campaign", back_populates="steps")
    contact_progress = relationship("ContactCampaignProgress", back_populates="current_step_obj")
    
    __table_args__ = (
        Index('idx_campaign_step_tenant', 'tenant_id'),
        Index('idx_campaign_step_campaign', 'campaign_id'),
        Index('idx_campaign_step_number', 'campaign_id', 'step_number'),
    )


class ContactCampaignProgress(Base):
    """Track progress of contacts through drip campaigns."""
    __tablename__ = "contact_campaign_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Progress tracking
    current_step = Column(Integer, default=1, nullable=False)
    current_step_id = Column(Integer, ForeignKey("campaign_steps.id"), nullable=True)
    
    # Status in campaign
    status = Column(String(50), nullable=False, default="active")  # active, completed, paused, unsubscribed, bounced
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_step_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Next action scheduled
    next_step_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Engagement metrics
    steps_completed = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    replies_received = Column(Integer, default=0, nullable=False)
    last_engagement_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    campaign_data = Column(JSON, default={}, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant")
    contact = relationship("Contact", back_populates="campaign_progress")
    campaign = relationship("Campaign", back_populates="contact_progress")
    current_step_obj = relationship("CampaignStep", foreign_keys=[current_step_id])
    
    __table_args__ = (
        Index('idx_progress_tenant', 'tenant_id'),
        Index('idx_progress_contact_campaign', 'contact_id', 'campaign_id'),
        Index('idx_progress_campaign', 'campaign_id'),
        Index('idx_progress_status', 'status'),
        Index('idx_progress_next_step', 'next_step_scheduled_at'),
    )
