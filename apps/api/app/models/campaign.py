"""Campaign model for managing WhatsApp marketing campaigns."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, Enum):
    """Campaign type enumeration."""
    BROADCAST = "broadcast"
    DRIP = "drip"
    TRIGGER = "trigger"
    FOLLOW_UP = "follow_up"


class Campaign(Base):
    """
    Campaign model for managing WhatsApp marketing campaigns.
    
    A campaign represents a marketing effort that sends messages to
    targeted contacts based on specific criteria and timing.
    """
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic campaign information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(String(20), nullable=False, default=CampaignType.BROADCAST)
    status = Column(String(20), nullable=False, default=CampaignStatus.DRAFT)
    
    # Campaign creator
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Targeting criteria (stored as JSON)
    target_criteria = Column(JSON, nullable=True)  # Tags, segments, etc.
    
    # Campaign settings
    message_template = Column(Text, nullable=False)
    personalization_fields = Column(JSON, nullable=True)  # Dynamic field mapping
    
    # Delivery settings
    send_immediately = Column(Boolean, default=False, nullable=False)
    respect_time_zones = Column(Boolean, default=True, nullable=False)
    send_time_start = Column(String(5), default="09:00", nullable=True)  # HH:MM format
    send_time_end = Column(String(5), default="18:00", nullable=True)  # HH:MM format
    
    # Analytics and tracking
    total_recipients = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    messages_delivered = Column(Integer, default=0, nullable=False)
    messages_read = Column(Integer, default=0, nullable=False)
    replies_received = Column(Integer, default=0, nullable=False)
    opt_outs = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="campaigns")
    messages = relationship("Message", back_populates="campaign", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index("idx_campaign_name", "name"),
        Index("idx_campaign_status", "status"),
        Index("idx_campaign_type", "type"),
        Index("idx_campaign_creator", "created_by"),
        Index("idx_campaign_scheduled", "scheduled_at"),
        Index("idx_campaign_created", "created_at"),
    )

    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if the campaign is currently active."""
        return self.status in [CampaignStatus.RUNNING, CampaignStatus.SCHEDULED]

    @property
    def delivery_rate(self) -> float:
        """Calculate the delivery rate as a percentage."""
        if self.messages_sent == 0:
            return 0.0
        return (self.messages_delivered / self.messages_sent) * 100

    @property
    def open_rate(self) -> float:
        """Calculate the open rate as a percentage."""
        if self.messages_delivered == 0:
            return 0.0
        return (self.messages_read / self.messages_delivered) * 100

    @property
    def reply_rate(self) -> float:
        """Calculate the reply rate as a percentage."""
        if self.messages_delivered == 0:
            return 0.0
        return (self.replies_received / self.messages_delivered) * 100

    def start(self) -> None:
        """Start the campaign."""
        self.status = CampaignStatus.RUNNING
        self.started_at = datetime.utcnow()

    def pause(self) -> None:
        """Pause the campaign."""
        self.status = CampaignStatus.PAUSED

    def complete(self) -> None:
        """Mark the campaign as completed."""
        self.status = CampaignStatus.COMPLETED
        self.ended_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel the campaign."""
        self.status = CampaignStatus.CANCELLED
        self.ended_at = datetime.utcnow()