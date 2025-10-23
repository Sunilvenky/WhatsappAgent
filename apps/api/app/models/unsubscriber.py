"""Unsubscriber model for tracking opt-out requests."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class UnsubscribeReason(str, Enum):
    """Unsubscribe reason enumeration."""
    NOT_INTERESTED = "not_interested"
    TOO_FREQUENT = "too_frequent"
    IRRELEVANT = "irrelevant"
    SPAM = "spam"
    CHANGED_MIND = "changed_mind"
    TECHNICAL_ISSUES = "technical_issues"
    OTHER = "other"


class UnsubscribeMethod(str, Enum):
    """Unsubscribe method enumeration."""
    REPLY = "reply"  # Replied with STOP/UNSUBSCRIBE
    CAMPAIGN_LINK = "campaign_link"  # Clicked unsubscribe link
    MANUAL = "manual"  # Manually unsubscribed by staff
    SYSTEM = "system"  # Automatically by system


class Unsubscriber(Base):
    """
    Unsubscriber model for tracking opt-out requests.
    
    This model tracks when and why contacts opt out of WhatsApp
    marketing communications for compliance and analysis.
    """
    __tablename__ = "unsubscribers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Unsubscriber relationships
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    
    # Unsubscribe details
    reason = Column(String(50), nullable=True)
    method = Column(String(20), nullable=False, default=UnsubscribeMethod.REPLY)
    feedback = Column(Text, nullable=True)  # Additional feedback from contact
    
    # Processing information
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # WhatsApp message that triggered unsubscribe (if applicable)
    trigger_message_content = Column(Text, nullable=True)
    trigger_whatsapp_id = Column(String(255), nullable=True)
    
    # Compliance tracking
    confirmation_sent = Column(DateTime(timezone=True), nullable=True)
    resubscribe_token = Column(String(255), nullable=True, unique=True, index=True)
    
    # Timestamps
    unsubscribed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    contact = relationship("Contact", back_populates="unsubscribers")
    campaign = relationship("Campaign")
    message = relationship("Message")
    processed_by_user = relationship("User", back_populates="processed_unsubscribers")

    # Indexes for performance
    __table_args__ = (
        Index("idx_unsubscriber_contact", "contact_id"),
        Index("idx_unsubscriber_campaign", "campaign_id"),
        Index("idx_unsubscriber_message", "message_id"),
        Index("idx_unsubscriber_reason", "reason"),
        Index("idx_unsubscriber_method", "method"),
        Index("idx_unsubscriber_date", "unsubscribed_at"),
        Index("idx_unsubscriber_token", "resubscribe_token"),
    )

    def __repr__(self):
        return f"<Unsubscriber(id={self.id}, contact_id={self.contact_id}, reason='{self.reason}')>"

    @property
    def is_manual_unsubscribe(self) -> bool:
        """Check if this was a manual unsubscribe."""
        return self.method == UnsubscribeMethod.MANUAL

    @property
    def is_reply_unsubscribe(self) -> bool:
        """Check if this was an unsubscribe via reply."""
        return self.method == UnsubscribeMethod.REPLY

    @property
    def has_resubscribe_token(self) -> bool:
        """Check if a resubscribe token exists."""
        return self.resubscribe_token is not None

    def generate_resubscribe_token(self) -> str:
        """Generate a unique resubscribe token."""
        import uuid
        self.resubscribe_token = str(uuid.uuid4())
        return self.resubscribe_token

    def mark_confirmation_sent(self) -> None:
        """Mark that confirmation was sent to the contact."""
        self.confirmation_sent = datetime.utcnow()

    def process(self, user_id: int) -> None:
        """Mark the unsubscribe as processed by a user."""
        self.processed_by = user_id