"""Pydantic schemas for Conversation model."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from apps.api.app.models.conversation import ConversationStatus


# Conversation schemas
class ConversationBase(BaseModel):
    """Base schema for Conversation."""
    subject: Optional[str] = Field(None, max_length=255)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    tags: Optional[str] = None
    notes: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    contact_id: int
    whatsapp_conversation_id: Optional[str] = Field(None, max_length=255)


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    subject: Optional[str] = Field(None, max_length=255)
    status: Optional[ConversationStatus] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    assigned_to: Optional[int] = None
    tags: Optional[str] = None
    notes: Optional[str] = None


class Conversation(ConversationBase):
    """Schema for Conversation response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contact_id: int
    assigned_to: Optional[int] = None
    status: ConversationStatus
    whatsapp_conversation_id: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_message_from_contact: bool
    unread_count: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    # Computed properties
    is_active: bool
    is_closed: bool
    has_unread_messages: bool
    is_urgent: bool


# Conversation assignment schemas
class ConversationAssignment(BaseModel):
    """Schema for assigning a conversation to a user."""
    assigned_to: int


class ConversationAction(BaseModel):
    """Schema for conversation actions."""
    action: str = Field(..., pattern="^(close|reopen|archive|mark_read)$")


# Conversation search and filter schemas
class ConversationSearch(BaseModel):
    """Schema for conversation search parameters."""
    assigned_to: Optional[int] = None
    status: Optional[ConversationStatus] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    has_unread: Optional[bool] = None
    search: Optional[str] = None
    skip: int = 0
    limit: int = 100


# Conversation with related data
class ConversationWithContact(Conversation):
    """Conversation schema with contact information."""
    contact: Optional[Dict[str, Any]] = None


class ConversationWithMessages(Conversation):
    """Conversation schema with recent messages."""
    messages: List[Dict[str, Any]] = []
    message_count: int = 0


class ConversationFull(Conversation):
    """Complete conversation schema with all related data."""
    contact: Optional[Dict[str, Any]] = None
    assigned_user: Optional[Dict[str, Any]] = None
    recent_messages: List[Dict[str, Any]] = []
    message_count: int = 0


# Conversation statistics schemas
class ConversationStats(BaseModel):
    """Schema for conversation statistics."""
    total_conversations: int
    active_conversations: int
    closed_conversations: int
    archived_conversations: int
    assigned_conversations: int
    unassigned_conversations: int
    with_unread: int
    urgent_conversations: int
    average_response_time: Optional[float] = None  # in hours


class UserConversationStats(BaseModel):
    """Schema for user-specific conversation statistics."""
    user_id: int
    assigned_conversations: int
    active_conversations: int
    with_unread: int
    urgent_conversations: int
    overdue_conversations: int
    avg_response_time: Optional[float] = None


# Conversation metrics schemas
class ConversationMetrics(BaseModel):
    """Schema for conversation metrics over time."""
    date: datetime
    new_conversations: int
    closed_conversations: int
    total_active: int
    avg_response_time: Optional[float] = None
    customer_satisfaction: Optional[float] = None


# Aliases for backwards compatibility
ConversationResponse = Conversation