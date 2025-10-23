"""CRUD operations for Reply model (extends Message)."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from apps.api.app.models.message import Message, MessageDirection


class ReplyCRUD:
    """CRUD operations for Reply model."""

    def create(self, db: Session, **reply_data) -> Message:
        """Create a new reply (message with direction=INBOUND)."""
        # Ensure it's marked as inbound
        reply_data['direction'] = MessageDirection.INBOUND
        reply = Message(**reply_data)
        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply

    def get(self, db: Session, reply_id: int) -> Optional[Message]:
        """Get a reply by ID."""
        return db.query(Message).filter(
            and_(
                Message.id == reply_id,
                Message.direction == MessageDirection.INBOUND
            )
        ).first()

    def get_conversation_replies(
        self, 
        db: Session, 
        conversation_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get all replies for a conversation."""
        return db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.direction == MessageDirection.INBOUND
            )
        ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

    def count_conversation_replies(self, db: Session, conversation_id: int) -> int:
        """Count replies in a conversation."""
        return db.query(Message).filter(
            and_(
                Message.conversation_id == conversation_id,
                Message.direction == MessageDirection.INBOUND
            )
        ).count()


# Global instance
reply_crud = ReplyCRUD()
