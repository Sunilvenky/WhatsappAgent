"""Reply model for tracking replies to campaign messages."""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class ReplyStatus(str, Enum):
    """Reply status enumeration."""
    NEW = "new"
    READ = "read"
    RESPONDED = "responded"
    ARCHIVED = "archived"


class ReplyType(str, Enum):
    """Reply type enumeration."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    QUESTION = "question"
    COMPLAINT = "complaint"
    NEUTRAL = "neutral"
    OPT_OUT = "opt_out"


class Reply(Base):
    """
    Reply model for tracking replies to campaign messages.
    
    This model specifically tracks incoming messages that are replies
    to outbound campaign messages, enabling response analysis.
    """
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Reply relationships
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    original_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    
    # Reply content
    content = Column(Text, nullable=False)
    whatsapp_message_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Reply classification
    reply_type = Column(String(20), nullable=True)  # Positive, negative, question, etc.
    sentiment_score = Column(String(10), nullable=True)  # positive, negative, neutral
    intent = Column(String(100), nullable=True)  # Customer intent (buy, info, support, etc.)
    
    # Processing status
    status = Column(String(20), nullable=False, default=ReplyStatus.NEW)
    is_processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # AI analysis (if available)
    ai_analysis = Column(JSON, nullable=True)  # AI-generated insights
    confidence_score = Column(String(10), nullable=True)  # AI confidence level
    
    # Response tracking
    requires_response = Column(Boolean, default=True, nullable=False)
    response_deadline = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    response_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="replies")
    original_message = relationship("Message", foreign_keys=[original_message_id])
    response_message = relationship("Message", foreign_keys=[response_message_id])
    processed_by_user = relationship("User", back_populates="processed_replies")

    # Indexes for performance
    __table_args__ = (
        Index("idx_reply_conversation", "conversation_id"),
        Index("idx_reply_original_message", "original_message_id"),
        Index("idx_reply_status", "status"),
        Index("idx_reply_type", "reply_type"),
        Index("idx_reply_processed", "is_processed"),
        Index("idx_reply_received", "received_at"),
        Index("idx_reply_requires_response", "requires_response"),
        Index("idx_reply_whatsapp_id", "whatsapp_message_id"),
    )

    def __repr__(self):
        return f"<Reply(id={self.id}, status='{self.status}', type='{self.reply_type}')>"

    @property
    def is_new(self) -> bool:
        """Check if this is a new reply."""
        return self.status == ReplyStatus.NEW

    @property
    def is_positive(self) -> bool:
        """Check if this is a positive reply."""
        return self.reply_type == ReplyType.POSITIVE

    @property
    def is_opt_out(self) -> bool:
        """Check if this is an opt-out reply."""
        return self.reply_type == ReplyType.OPT_OUT

    @property
    def is_overdue(self) -> bool:
        """Check if the reply response is overdue."""
        if not self.requires_response or self.responded_at:
            return False
        if not self.response_deadline:
            return False
        return datetime.utcnow() > self.response_deadline

    def mark_as_read(self) -> None:
        """Mark the reply as read."""
        if self.status == ReplyStatus.NEW:
            self.status = ReplyStatus.READ

    def mark_as_responded(self, response_message_id: int = None) -> None:
        """Mark the reply as responded to."""
        self.status = ReplyStatus.RESPONDED
        self.responded_at = datetime.utcnow()
        if response_message_id:
            self.response_message_id = response_message_id

    def process(self, user_id: int, reply_type: str = None, sentiment: str = None) -> None:
        """Mark the reply as processed by a user."""
        self.is_processed = True
        self.processed_at = datetime.utcnow()
        self.processed_by = user_id
        if reply_type:
            self.reply_type = reply_type
        if sentiment:
            self.sentiment_score = sentiment

    def archive(self) -> None:
        """Archive the reply."""
        self.status = ReplyStatus.ARCHIVED

    def set_ai_analysis(self, analysis: dict, confidence: str = None) -> None:
        """Set AI analysis results for the reply."""
        self.ai_analysis = analysis
        if confidence:
            self.confidence_score = confidence