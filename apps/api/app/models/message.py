"""Message model for tracking individual WhatsApp messages."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class MessageStatus(str, Enum):
    """Message status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    """Message type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    TEMPLATE = "template"


class MessageDirection(str, Enum):
    """Message direction enumeration."""
    OUTBOUND = "outbound"  # Sent to contact
    INBOUND = "inbound"    # Received from contact


class Message(Base):
    """
    Message model for tracking individual WhatsApp messages.
    
    This model stores all messages sent through campaigns or individual
    conversations, including delivery status and metadata.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Message relationships
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    phone_number_id = Column(Integer, ForeignKey("phone_numbers.id", ondelete="CASCADE"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default=MessageType.TEXT)
    direction = Column(String(10), nullable=False, default=MessageDirection.OUTBOUND)
    
    # WhatsApp metadata
    whatsapp_message_id = Column(String(255), nullable=True, unique=True, index=True)
    whatsapp_status = Column(String(20), nullable=True)  # WhatsApp API status
    
    # Delivery tracking
    status = Column(String(20), nullable=False, default=MessageStatus.PENDING)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Media and attachments
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)
    media_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Template information (for template messages)
    template_name = Column(String(255), nullable=True)
    template_variables = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
    phone_number = relationship("PhoneNumber", back_populates="messages")

    # Indexes for performance
    __table_args__ = (
        Index("idx_message_campaign", "campaign_id"),
        Index("idx_message_conversation", "conversation_id"),
        Index("idx_message_phone", "phone_number_id"),
        Index("idx_message_status", "status"),
        Index("idx_message_direction", "direction"),
        Index("idx_message_created", "created_at"),
        Index("idx_message_sent", "sent_at"),
        Index("idx_message_whatsapp_id", "whatsapp_message_id"),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, status='{self.status}', direction='{self.direction}')>"

    @property
    def is_outbound(self) -> bool:
        """Check if this is an outbound message."""
        return self.direction == MessageDirection.OUTBOUND

    @property
    def is_inbound(self) -> bool:
        """Check if this is an inbound message."""
        return self.direction == MessageDirection.INBOUND

    @property
    def is_delivered(self) -> bool:
        """Check if the message has been delivered."""
        return self.status in [MessageStatus.DELIVERED, MessageStatus.READ]

    @property
    def is_failed(self) -> bool:
        """Check if the message has failed."""
        return self.status == MessageStatus.FAILED

    @property
    def can_retry(self) -> bool:
        """Check if the message can be retried."""
        return self.is_failed and self.retry_count < self.max_retries

    def mark_sent(self, whatsapp_message_id: str = None) -> None:
        """Mark the message as sent."""
        self.status = MessageStatus.SENT
        self.sent_at = datetime.utcnow()
        if whatsapp_message_id:
            self.whatsapp_message_id = whatsapp_message_id

    def mark_delivered(self) -> None:
        """Mark the message as delivered."""
        self.status = MessageStatus.DELIVERED
        self.delivered_at = datetime.utcnow()

    def mark_read(self) -> None:
        """Mark the message as read."""
        self.status = MessageStatus.READ
        self.read_at = datetime.utcnow()

    def mark_failed(self, error_code: str = None, error_message: str = None) -> None:
        """Mark the message as failed."""
        self.status = MessageStatus.FAILED
        self.failed_at = datetime.utcnow()
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message

    def increment_retry(self) -> None:
        """Increment the retry count."""
        self.retry_count += 1
        self.status = MessageStatus.PENDING