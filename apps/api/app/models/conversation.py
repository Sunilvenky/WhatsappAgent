"""Conversation model for tracking WhatsApp conversations."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Conversation(Base):
    """
    Conversation model for tracking WhatsApp conversations.
    
    A conversation represents a thread of messages between the business
    and a contact, providing context for message history.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Conversation relationships
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Conversation metadata
    subject = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default=ConversationStatus.ACTIVE)
    priority = Column(String(10), default="medium", nullable=False)  # low, medium, high, urgent
    
    # WhatsApp conversation ID (if available)
    whatsapp_conversation_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Conversation tracking
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    last_message_from_contact = Column(Boolean, default=False, nullable=False)
    unread_count = Column(Integer, default=0, nullable=False)
    
    # Tags and notes
    tags = Column(Text, nullable=True)  # JSON string for flexible tagging
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    contact = relationship("Contact", back_populates="conversations")
    assigned_user = relationship("User", back_populates="assigned_conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    replies = relationship("Reply", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index("idx_conversation_contact", "contact_id"),
        Index("idx_conversation_assigned", "assigned_to"),
        Index("idx_conversation_status", "status"),
        Index("idx_conversation_last_message", "last_message_at"),
        Index("idx_conversation_priority", "priority"),
        Index("idx_conversation_created", "created_at"),
        Index("idx_conversation_whatsapp_id", "whatsapp_conversation_id"),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, contact_id={self.contact_id}, status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if the conversation is active."""
        return self.status == ConversationStatus.ACTIVE

    @property
    def is_closed(self) -> bool:
        """Check if the conversation is closed."""
        return self.status == ConversationStatus.CLOSED

    @property
    def has_unread_messages(self) -> bool:
        """Check if the conversation has unread messages."""
        return self.unread_count > 0

    @property
    def is_urgent(self) -> bool:
        """Check if the conversation is marked as urgent."""
        return self.priority == "urgent"

    def close(self) -> None:
        """Close the conversation."""
        self.status = ConversationStatus.CLOSED
        self.closed_at = datetime.utcnow()

    def reopen(self) -> None:
        """Reopen the conversation."""
        self.status = ConversationStatus.ACTIVE
        self.closed_at = None

    def archive(self) -> None:
        """Archive the conversation."""
        self.status = ConversationStatus.ARCHIVED

    def mark_as_read(self) -> None:
        """Mark all messages in the conversation as read."""
        self.unread_count = 0

    def assign_to(self, user_id: int) -> None:
        """Assign the conversation to a user."""
        self.assigned_to = user_id

    def update_last_message(self, from_contact: bool = False) -> None:
        """Update the last message timestamp and sender."""
        self.last_message_at = datetime.utcnow()
        self.last_message_from_contact = from_contact
        if from_contact:
            self.unread_count += 1