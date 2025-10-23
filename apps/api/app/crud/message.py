"""CRUD operations for Message model."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from apps.api.app.models.message import Message, MessageStatus, MessageDirection, MessageType


class MessageCRUD:
    """CRUD operations for Message model."""

    def create(self, db: Session, **message_data) -> Message:
        """Create a new message."""
        message = Message(**message_data)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get(self, db: Session, message_id: int) -> Optional[Message]:
        """Get a message by ID."""
        return db.query(Message).filter(Message.id == message_id).first()

    def get_by_whatsapp_id(self, db: Session, whatsapp_message_id: str) -> Optional[Message]:
        """Get a message by WhatsApp message ID."""
        return db.query(Message).filter(
            Message.whatsapp_message_id == whatsapp_message_id
        ).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        campaign_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        phone_number_id: Optional[int] = None,
        status: Optional[MessageStatus] = None,
        direction: Optional[MessageDirection] = None
    ) -> List[Message]:
        """Get multiple messages with optional filtering."""
        query = db.query(Message)
        
        if campaign_id:
            query = query.filter(Message.campaign_id == campaign_id)
            
        if conversation_id:
            query = query.filter(Message.conversation_id == conversation_id)
            
        if phone_number_id:
            query = query.filter(Message.phone_number_id == phone_number_id)
            
        if status:
            query = query.filter(Message.status == status)
            
        if direction:
            query = query.filter(Message.direction == direction)
        
        return query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, db: Session, message: Message, **update_data) -> Message:
        """Update a message."""
        for field, value in update_data.items():
            if hasattr(message, field):
                setattr(message, field, value)
        
        db.commit()
        db.refresh(message)
        return message

    def delete(self, db: Session, message_id: int) -> bool:
        """Delete a message."""
        message = self.get(db, message_id)
        if message:
            db.delete(message)
            db.commit()
            return True
        return False

    def get_conversation_messages(
        self, 
        db: Session, 
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages for a specific conversation."""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

    def get_campaign_messages(
        self, 
        db: Session, 
        campaign_id: int,
        status: Optional[MessageStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages for a specific campaign."""
        query = db.query(Message).filter(Message.campaign_id == campaign_id)
        
        if status:
            query = query.filter(Message.status == status)
        
        return query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

    def get_pending_messages(self, db: Session, limit: int = 100) -> List[Message]:
        """Get messages that are pending to be sent."""
        return db.query(Message).filter(
            Message.status == MessageStatus.PENDING
        ).order_by(Message.created_at.asc()).limit(limit).all()

    def get_failed_messages(self, db: Session, can_retry: bool = True) -> List[Message]:
        """Get failed messages, optionally only those that can be retried."""
        query = db.query(Message).filter(Message.status == MessageStatus.FAILED)
        
        if can_retry:
            query = query.filter(Message.retry_count < Message.max_retries)
        
        return query.all()

    def mark_sent(
        self, 
        db: Session, 
        message_id: int, 
        whatsapp_message_id: Optional[str] = None
    ) -> bool:
        """Mark a message as sent."""
        message = self.get(db, message_id)
        if message:
            message.mark_sent(whatsapp_message_id)
            db.commit()
            return True
        return False

    def mark_delivered(self, db: Session, message_id: int) -> bool:
        """Mark a message as delivered."""
        message = self.get(db, message_id)
        if message:
            message.mark_delivered()
            db.commit()
            return True
        return False

    def mark_read(self, db: Session, message_id: int) -> bool:
        """Mark a message as read."""
        message = self.get(db, message_id)
        if message:
            message.mark_read()
            db.commit()
            return True
        return False

    def mark_failed(
        self, 
        db: Session, 
        message_id: int,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Mark a message as failed."""
        message = self.get(db, message_id)
        if message:
            message.mark_failed(error_code, error_message)
            db.commit()
            return True
        return False

    def retry_message(self, db: Session, message_id: int) -> bool:
        """Retry a failed message."""
        message = self.get(db, message_id)
        if message and message.can_retry:
            message.increment_retry()
            db.commit()
            return True
        return False

    def update_whatsapp_status(
        self, 
        db: Session, 
        whatsapp_message_id: str,
        status: str
    ) -> bool:
        """Update message status based on WhatsApp webhook."""
        message = self.get_by_whatsapp_id(db, whatsapp_message_id)
        if not message:
            return False
        
        message.whatsapp_status = status
        
        # Map WhatsApp status to our internal status
        if status == "sent":
            message.mark_sent()
        elif status == "delivered":
            message.mark_delivered()
        elif status == "read":
            message.mark_read()
        elif status in ["failed", "undelivered"]:
            message.mark_failed()
        
        db.commit()
        return True

    def get_message_stats(
        self, 
        db: Session,
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get message statistics."""
        query = db.query(Message)
        
        if campaign_id:
            query = query.filter(Message.campaign_id == campaign_id)
            
        if start_date:
            query = query.filter(Message.created_at >= start_date)
            
        if end_date:
            query = query.filter(Message.created_at <= end_date)
        
        messages = query.all()
        
        stats = {
            "total": len(messages),
            "pending": sum(1 for m in messages if m.status == MessageStatus.PENDING),
            "sent": sum(1 for m in messages if m.status == MessageStatus.SENT),
            "delivered": sum(1 for m in messages if m.status == MessageStatus.DELIVERED),
            "read": sum(1 for m in messages if m.status == MessageStatus.READ),
            "failed": sum(1 for m in messages if m.status == MessageStatus.FAILED),
            "outbound": sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND),
            "inbound": sum(1 for m in messages if m.direction == MessageDirection.INBOUND),
        }
        
        return stats

    def count(
        self, 
        db: Session,
        campaign_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        status: Optional[MessageStatus] = None,
        direction: Optional[MessageDirection] = None
    ) -> int:
        """Count messages with optional filtering."""
        query = db.query(Message)
        
        if campaign_id:
            query = query.filter(Message.campaign_id == campaign_id)
            
        if conversation_id:
            query = query.filter(Message.conversation_id == conversation_id)
            
        if status:
            query = query.filter(Message.status == status)
            
        if direction:
            query = query.filter(Message.direction == direction)
        
        return query.count()


# Global instance
message_crud = MessageCRUD()


# Helper functions for workers
def create_message(db: Session, message_data: dict) -> Message:
    """Create a message (helper for workers)."""
    return message_crud.create(db, **message_data)


def get_message(db: Session, message_id: int) -> Optional[Message]:
    """Get a message by ID (helper for workers)."""
    return message_crud.get(db, message_id)


def update_message(db: Session, message_id: int, update_data: dict) -> Optional[Message]:
    """Update a message (helper for workers)."""
    message = message_crud.get(db, message_id)
    if message:
        return message_crud.update(db, message, **update_data)
    return None


def get_message_by_external_id(db: Session, external_id: str) -> Optional[Message]:
    """Get message by external/WhatsApp ID."""
    return message_crud.get_by_whatsapp_id(db, external_id)


def get_messages_by_conversation(db: Session, conversation_id: int) -> List[Message]:
    """Get all messages in a conversation."""
    return message_crud.get_conversation_messages(db, conversation_id, limit=1000)


def get_messages_by_contact(db: Session, contact_id: int, campaign_id: Optional[int] = None) -> List[Message]:
    """Get messages sent to a contact."""
    query = db.query(Message).filter(Message.contact_id == contact_id)
    if campaign_id:
        query = query.filter(Message.campaign_id == campaign_id)
    return query.order_by(Message.created_at.desc()).all()


def get_recent_messages(db: Session, phone_number_id: int, hours: int = 24) -> List[Message]:
    """Get recent messages from a phone number."""
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return db.query(Message).filter(
        Message.phone_number_id == phone_number_id,
        Message.sent_at >= cutoff
    ).order_by(Message.sent_at.desc()).all()


def delete_messages_before(db: Session, cutoff_date: datetime) -> int:
    """Delete messages older than cutoff date."""
    result = db.query(Message).filter(Message.created_at < cutoff_date).delete()
    db.commit()
    return result