"""Pydantic schemas for Message model."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from apps.api.app.models.message import MessageStatus, MessageType, MessageDirection


# Message schemas
class MessageBase(BaseModel):
    """Base schema for Message."""
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT
    direction: MessageDirection = MessageDirection.OUTBOUND
    media_url: Optional[str] = Field(None, max_length=500)
    media_type: Optional[str] = Field(None, max_length=50)
    template_name: Optional[str] = Field(None, max_length=255)
    template_variables: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    conversation_id: int
    phone_number_id: int
    campaign_id: Optional[int] = None


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[MessageStatus] = None
    whatsapp_message_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class Message(MessageBase):
    """Schema for Message response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    campaign_id: Optional[int] = None
    conversation_id: int
    phone_number_id: int
    status: MessageStatus
    whatsapp_message_id: Optional[str] = None
    whatsapp_status: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    media_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_outbound: bool
    is_inbound: bool
    is_delivered: bool
    is_failed: bool
    can_retry: bool


# Message status update schemas
class MessageStatusUpdate(BaseModel):
    """Schema for updating message status via webhook."""
    whatsapp_message_id: str
    status: str
    timestamp: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class MessageRetry(BaseModel):
    """Schema for retrying a failed message."""
    max_retries: Optional[int] = Field(None, ge=1, le=10)


# Message search and filter schemas
class MessageSearch(BaseModel):
    """Schema for message search parameters."""
    campaign_id: Optional[int] = None
    conversation_id: Optional[int] = None
    phone_number_id: Optional[int] = None
    status: Optional[MessageStatus] = None
    direction: Optional[MessageDirection] = None
    message_type: Optional[MessageType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


# Message statistics schemas
class MessageStats(BaseModel):
    """Schema for message statistics."""
    total: int
    pending: int
    sent: int
    delivered: int
    read: int
    failed: int
    outbound: int
    inbound: int
    delivery_rate: float
    read_rate: float
    failure_rate: float


# Bulk message schemas
class BulkMessageCreate(BaseModel):
    """Schema for creating bulk messages."""
    campaign_id: Optional[int] = None
    phone_number_ids: List[int] = Field(..., min_items=1)
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT
    schedule_for: Optional[datetime] = None


class BulkMessageResult(BaseModel):
    """Schema for bulk message creation result."""
    created_count: int
    failed_count: int
    created_message_ids: List[int]
    errors: List[str]


# Template message schemas
class TemplateMessage(BaseModel):
    """Schema for template-based messages."""
    template_name: str = Field(..., max_length=255)
    template_variables: Dict[str, Any]
    phone_number_ids: List[int] = Field(..., min_items=1)
    campaign_id: Optional[int] = None


# Message with conversation context
class MessageWithContext(Message):
    """Message schema with conversation context."""
    conversation: Optional[Dict[str, Any]] = None
    contact: Optional[Dict[str, Any]] = None
    phone_number: Optional[Dict[str, Any]] = None


# Aliases for backwards compatibility
MessageResponse = Message
ReplyResponse = Message  # Used for conversation replies
ReplyCreate = MessageCreate  # Replies use the same creation schema