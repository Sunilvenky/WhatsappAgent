"""CRUD operations for Conversation model."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from apps.api.app.models.conversation import Conversation, ConversationStatus


class ConversationCRUD:
    """CRUD operations for Conversation model."""

    def create(self, db: Session, **conversation_data) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(**conversation_data)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_by_contact(self, db: Session, contact_id: int) -> List[Conversation]:
        """Get all conversations for a contact."""
        return db.query(Conversation).filter(
            Conversation.contact_id == contact_id
        ).order_by(Conversation.last_message_at.desc()).all()

    def get_active_by_contact(self, db: Session, contact_id: int) -> Optional[Conversation]:
        """Get the active conversation for a contact."""
        return db.query(Conversation).filter(
            and_(
                Conversation.contact_id == contact_id,
                Conversation.status == ConversationStatus.ACTIVE
            )
        ).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        assigned_to: Optional[int] = None,
        status: Optional[ConversationStatus] = None,
        priority: Optional[str] = None,
        has_unread: Optional[bool] = None,
        contact_id: Optional[int] = None
    ) -> List[Conversation]:
        """Get multiple conversations with optional filtering."""
        query = db.query(Conversation)
        
        if contact_id:
            query = query.filter(Conversation.contact_id == contact_id)
            
        if assigned_to:
            query = query.filter(Conversation.assigned_to == assigned_to)
            
        if status:
            query = query.filter(Conversation.status == status)
            
        if priority:
            query = query.filter(Conversation.priority == priority)
            
        if has_unread is not None:
            if has_unread:
                query = query.filter(Conversation.unread_count > 0)
            else:
                query = query.filter(Conversation.unread_count == 0)
        
        return query.order_by(Conversation.last_message_at.desc()).offset(skip).limit(limit).all()

    def update(self, db: Session, conversation: Conversation, **update_data) -> Conversation:
        """Update a conversation."""
        for field, value in update_data.items():
            if hasattr(conversation, field):
                setattr(conversation, field, value)
        
        db.commit()
        db.refresh(conversation)
        return conversation

    def delete(self, db: Session, conversation_id: int) -> bool:
        """Delete a conversation."""
        conversation = self.get(db, conversation_id)
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False

    def get_assigned_conversations(
        self, 
        db: Session, 
        user_id: int,
        status: Optional[ConversationStatus] = None
    ) -> List[Conversation]:
        """Get conversations assigned to a user."""
        query = db.query(Conversation).filter(Conversation.assigned_to == user_id)
        
        if status:
            query = query.filter(Conversation.status == status)
        
        return query.order_by(Conversation.last_message_at.desc()).all()

    def get_unassigned_conversations(self, db: Session) -> List[Conversation]:
        """Get conversations that are not assigned to anyone."""
        return db.query(Conversation).filter(
            and_(
                Conversation.assigned_to.is_(None),
                Conversation.status == ConversationStatus.ACTIVE
            )
        ).order_by(Conversation.last_message_at.desc()).all()

    def get_conversations_with_unread(self, db: Session, user_id: Optional[int] = None) -> List[Conversation]:
        """Get conversations with unread messages."""
        query = db.query(Conversation).filter(Conversation.unread_count > 0)
        
        if user_id:
            query = query.filter(Conversation.assigned_to == user_id)
        
        return query.order_by(Conversation.last_message_at.desc()).all()

    def get_urgent_conversations(self, db: Session, user_id: Optional[int] = None) -> List[Conversation]:
        """Get urgent conversations."""
        query = db.query(Conversation).filter(
            and_(
                Conversation.priority == "urgent",
                Conversation.status == ConversationStatus.ACTIVE
            )
        )
        
        if user_id:
            query = query.filter(Conversation.assigned_to == user_id)
        
        return query.order_by(Conversation.last_message_at.desc()).all()

    def assign_conversation(self, db: Session, conversation_id: int, user_id: int) -> bool:
        """Assign a conversation to a user."""
        conversation = self.get(db, conversation_id)
        if conversation:
            conversation.assign_to(user_id)
            db.commit()
            return True
        return False

    def close_conversation(self, db: Session, conversation_id: int) -> bool:
        """Close a conversation."""
        conversation = self.get(db, conversation_id)
        if conversation and conversation.is_active:
            conversation.close()
            db.commit()
            return True
        return False

    def reopen_conversation(self, db: Session, conversation_id: int) -> bool:
        """Reopen a conversation."""
        conversation = self.get(db, conversation_id)
        if conversation and conversation.is_closed:
            conversation.reopen()
            db.commit()
            return True
        return False

    def archive_conversation(self, db: Session, conversation_id: int) -> bool:
        """Archive a conversation."""
        conversation = self.get(db, conversation_id)
        if conversation:
            conversation.archive()
            db.commit()
            return True
        return False

    def mark_as_read(self, db: Session, conversation_id: int) -> bool:
        """Mark all messages in a conversation as read."""
        conversation = self.get(db, conversation_id)
        if conversation:
            conversation.mark_as_read()
            db.commit()
            return True
        return False

    def update_last_message(
        self, 
        db: Session, 
        conversation_id: int,
        from_contact: bool = False
    ) -> bool:
        """Update the last message timestamp and increment unread count if from contact."""
        conversation = self.get(db, conversation_id)
        if conversation:
            conversation.update_last_message(from_contact)
            db.commit()
            return True
        return False

    def get_or_create_for_contact(
        self, 
        db: Session, 
        contact_id: int,
        whatsapp_conversation_id: Optional[str] = None
    ) -> Conversation:
        """Get existing active conversation or create new one for contact."""
        # Try to find existing active conversation
        conversation = self.get_active_by_contact(db, contact_id)
        
        if not conversation:
            # Create new conversation
            conversation_data = {
                "contact_id": contact_id,
                "status": ConversationStatus.ACTIVE
            }
            if whatsapp_conversation_id:
                conversation_data["whatsapp_conversation_id"] = whatsapp_conversation_id
            
            conversation = self.create(db, **conversation_data)
        
        return conversation

    def search_conversations(
        self, 
        db: Session, 
        query: str,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Search conversations by subject or notes."""
        search_filter = or_(
            Conversation.subject.ilike(f"%{query}%"),
            Conversation.notes.ilike(f"%{query}%")
        )
        
        db_query = db.query(Conversation).filter(search_filter)
        
        if user_id:
            db_query = db_query.filter(Conversation.assigned_to == user_id)
        
        return db_query.order_by(Conversation.last_message_at.desc()).offset(skip).limit(limit).all()

    def count(
        self, 
        db: Session,
        assigned_to: Optional[int] = None,
        status: Optional[ConversationStatus] = None,
        has_unread: Optional[bool] = None
    ) -> int:
        """Count conversations with optional filtering."""
        query = db.query(Conversation)
        
        if assigned_to:
            query = query.filter(Conversation.assigned_to == assigned_to)
            
        if status:
            query = query.filter(Conversation.status == status)
            
        if has_unread is not None:
            if has_unread:
                query = query.filter(Conversation.unread_count > 0)
            else:
                query = query.filter(Conversation.unread_count == 0)
        
        return query.count()


# Global instance
conversation_crud = ConversationCRUD()