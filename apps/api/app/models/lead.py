"""Lead model for tracking potential customers and sales opportunities."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, Boolean, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class LeadStatus(str, Enum):
    """Lead status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NURTURING = "nurturing"


class LeadSource(str, Enum):
    """Lead source enumeration."""
    WHATSAPP_CAMPAIGN = "whatsapp_campaign"
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    PHONE = "phone"
    EVENT = "event"
    ADVERTISEMENT = "advertisement"
    OTHER = "other"


class LeadPriority(str, Enum):
    """Lead priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Lead(Base):
    """
    Lead model for tracking potential customers and sales opportunities.
    
    This model tracks leads generated through WhatsApp campaigns and
    other sources, managing the sales pipeline and conversion tracking.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Lead relationships
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    
    # Lead information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=LeadStatus.NEW)
    priority = Column(String(10), nullable=False, default=LeadPriority.MEDIUM)
    source = Column(String(50), nullable=False, default=LeadSource.WHATSAPP_CAMPAIGN)
    
    # Financial information
    estimated_value = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    probability = Column(Integer, default=10, nullable=False)  # Percentage 0-100
    
    # Timeline
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    actual_close_date = Column(DateTime(timezone=True), nullable=True)
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    next_follow_up = Column(DateTime(timezone=True), nullable=True)
    
    # Lead scoring and qualification
    lead_score = Column(Integer, default=0, nullable=False)  # 0-100 scoring system
    qualification_notes = Column(Text, nullable=True)
    pain_points = Column(JSON, nullable=True)  # Array of identified pain points
    budget_range = Column(String(100), nullable=True)
    decision_maker = Column(Boolean, default=False, nullable=False)
    
    # Tracking and analytics
    conversion_source = Column(String(100), nullable=True)  # What converted them
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    
    # Notes and activities
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string for flexible tagging
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    contact = relationship("Contact", back_populates="leads")
    assigned_user = relationship("User", back_populates="assigned_leads")
    campaign = relationship("Campaign")

    # Indexes for performance
    __table_args__ = (
        Index("idx_lead_contact", "contact_id"),
        Index("idx_lead_assigned", "assigned_to"),
        Index("idx_lead_campaign", "campaign_id"),
        Index("idx_lead_status", "status"),
        Index("idx_lead_priority", "priority"),
        Index("idx_lead_source", "source"),
        Index("idx_lead_score", "lead_score"),
        Index("idx_lead_expected_close", "expected_close_date"),
        Index("idx_lead_created", "created_at"),
        Index("idx_lead_title", "title"),
    )

    def __repr__(self):
        return f"<Lead(id={self.id}, title='{self.title}', status='{self.status}')>"

    @property
    def is_open(self) -> bool:
        """Check if the lead is still open."""
        return self.status not in [LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST]

    @property
    def is_won(self) -> bool:
        """Check if the lead was won."""
        return self.status == LeadStatus.CLOSED_WON

    @property
    def is_lost(self) -> bool:
        """Check if the lead was lost."""
        return self.status == LeadStatus.CLOSED_LOST

    @property
    def is_hot(self) -> bool:
        """Check if this is a hot lead (high priority or high score)."""
        return self.priority in [LeadPriority.HIGH, LeadPriority.URGENT] or self.lead_score >= 80

    @property
    def expected_revenue(self) -> float:
        """Calculate expected revenue based on value and probability."""
        if self.estimated_value and self.probability:
            return float(self.estimated_value) * (self.probability / 100)
        return 0.0

    @property
    def days_since_created(self) -> int:
        """Get the number of days since the lead was created."""
        return (datetime.utcnow() - self.created_at.replace(tzinfo=None)).days

    @property
    def is_overdue(self) -> bool:
        """Check if the lead follow-up is overdue."""
        if not self.next_follow_up:
            return False
        return datetime.utcnow() > self.next_follow_up.replace(tzinfo=None)

    def close_won(self, actual_value: float = None) -> None:
        """Mark the lead as closed won."""
        self.status = LeadStatus.CLOSED_WON
        self.actual_close_date = datetime.utcnow()
        self.probability = 100
        if actual_value:
            self.estimated_value = actual_value

    def close_lost(self, reason: str = None) -> None:
        """Mark the lead as closed lost."""
        self.status = LeadStatus.CLOSED_LOST
        self.actual_close_date = datetime.utcnow()
        self.probability = 0
        if reason and self.notes:
            self.notes += f"\n\nLost reason: {reason}"
        elif reason:
            self.notes = f"Lost reason: {reason}"

    def assign_to(self, user_id: int) -> None:
        """Assign the lead to a user."""
        self.assigned_to = user_id

    def update_score(self, score: int) -> None:
        """Update the lead score (0-100)."""
        self.lead_score = max(0, min(100, score))

    def schedule_follow_up(self, follow_up_date: datetime) -> None:
        """Schedule the next follow-up."""
        self.next_follow_up = follow_up_date

    def mark_contacted(self) -> None:
        """Mark the lead as contacted."""
        self.last_contact_date = datetime.utcnow()
        if self.status == LeadStatus.NEW:
            self.status = LeadStatus.CONTACTED