"""Tests for Message, Conversation, and Lead models."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from apps.api.app.models.contact import Contact
from apps.api.app.models.phone_number import PhoneNumber
from apps.api.app.models.conversation import Conversation, ConversationStatus
from apps.api.app.models.message import Message, MessageStatus, MessageDirection, MessageType
from apps.api.app.models.lead import Lead, LeadStatus, LeadSource, LeadPriority
from apps.api.app.models.user import User, UserRole
from apps.api.app.crud.conversation import conversation_crud
from apps.api.app.crud.message import message_crud
from apps.api.app.crud.lead import lead_crud
from apps.api.app.auth.utils import get_password_hash


class TestConversationModel:
    """Test Conversation model functionality."""

    def test_create_conversation(self, db: Session):
        """Test creating a conversation."""
        # Create a contact first
        contact = Contact(first_name="John", email="john@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        conversation_data = {
            "contact_id": contact.id,
            "subject": "Test Conversation",
            "status": ConversationStatus.ACTIVE,
            "priority": "high",
        }
        
        conversation = Conversation(**conversation_data)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.contact_id == contact.id
        assert conversation.subject == "Test Conversation"
        assert conversation.is_active is True
        assert conversation.is_urgent is True

    def test_conversation_close_reopen(self, db: Session):
        """Test closing and reopening a conversation."""
        contact = Contact(first_name="Jane", email="jane@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        conversation = Conversation(
            contact_id=contact.id,
            status=ConversationStatus.ACTIVE
        )
        db.add(conversation)
        db.commit()
        
        # Close conversation
        conversation.close()
        db.commit()
        
        assert conversation.status == ConversationStatus.CLOSED
        assert conversation.closed_at is not None
        assert conversation.is_closed is True
        
        # Reopen conversation
        conversation.reopen()
        db.commit()
        
        assert conversation.status == ConversationStatus.ACTIVE
        assert conversation.closed_at is None
        assert conversation.is_active is True

    def test_conversation_message_tracking(self, db: Session):
        """Test conversation message tracking."""
        contact = Contact(first_name="Bob", email="bob@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        conversation = Conversation(
            contact_id=contact.id,
            unread_count=0
        )
        db.add(conversation)
        db.commit()
        
        # Update last message from contact
        conversation.update_last_message(from_contact=True)
        db.commit()
        
        assert conversation.last_message_from_contact is True
        assert conversation.unread_count == 1
        assert conversation.has_unread_messages is True
        
        # Mark as read
        conversation.mark_as_read()
        db.commit()
        
        assert conversation.unread_count == 0
        assert conversation.has_unread_messages is False


class TestMessageModel:
    """Test Message model functionality."""

    def test_create_message(self, db: Session):
        """Test creating a message."""
        # Setup required objects
        contact = Contact(first_name="Alice", email="alice@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone = PhoneNumber(
            contact_id=contact.id,
            number="+1234567890",
            country_code="+1"
        )
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        conversation = Conversation(contact_id=contact.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        message_data = {
            "conversation_id": conversation.id,
            "phone_number_id": phone.id,
            "content": "Hello, this is a test message!",
            "message_type": MessageType.TEXT,
            "direction": MessageDirection.OUTBOUND,
        }
        
        message = Message(**message_data)
        db.add(message)
        db.commit()
        db.refresh(message)
        
        assert message.id is not None
        assert message.content == "Hello, this is a test message!"
        assert message.is_outbound is True
        assert message.is_inbound is False
        assert message.status == MessageStatus.PENDING

    def test_message_status_updates(self, db: Session):
        """Test message status update methods."""
        contact = Contact(first_name="Status", email="status@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone = PhoneNumber(contact_id=contact.id, number="+1111111111", country_code="+1")
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        conversation = Conversation(contact_id=contact.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        message = Message(
            conversation_id=conversation.id,
            phone_number_id=phone.id,
            content="Status test message",
            status=MessageStatus.PENDING
        )
        db.add(message)
        db.commit()
        
        # Mark as sent
        message.mark_sent("whatsapp_msg_123")
        db.commit()
        
        assert message.status == MessageStatus.SENT
        assert message.whatsapp_message_id == "whatsapp_msg_123"
        assert message.sent_at is not None
        
        # Mark as delivered
        message.mark_delivered()
        db.commit()
        
        assert message.status == MessageStatus.DELIVERED
        assert message.delivered_at is not None
        assert message.is_delivered is True
        
        # Mark as read
        message.mark_read()
        db.commit()
        
        assert message.status == MessageStatus.READ
        assert message.read_at is not None

    def test_message_retry_logic(self, db: Session):
        """Test message retry functionality."""
        contact = Contact(first_name="Retry", email="retry@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone = PhoneNumber(contact_id=contact.id, number="+2222222222", country_code="+1")
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        conversation = Conversation(contact_id=contact.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        message = Message(
            conversation_id=conversation.id,
            phone_number_id=phone.id,
            content="Retry test message",
            max_retries=3
        )
        db.add(message)
        db.commit()
        
        # Mark as failed
        message.mark_failed("ERROR_001", "Network timeout")
        db.commit()
        
        assert message.status == MessageStatus.FAILED
        assert message.is_failed is True
        assert message.can_retry is True
        assert message.error_code == "ERROR_001"
        
        # Increment retry
        message.increment_retry()
        db.commit()
        
        assert message.retry_count == 1
        assert message.status == MessageStatus.PENDING
        assert message.can_retry is True
        
        # Exhaust retries
        for i in range(2):
            message.mark_failed()
            message.increment_retry()
            db.commit()
        
        assert message.retry_count == 3
        assert message.can_retry is False


class TestLeadModel:
    """Test Lead model functionality."""

    def test_create_lead(self, db: Session):
        """Test creating a lead."""
        # Setup required objects
        contact = Contact(first_name="Lead", last_name="Contact", email="lead@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        user = User(
            email="sales@example.com",
            username="sales",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        lead_data = {
            "contact_id": contact.id,
            "assigned_to": user.id,
            "title": "Enterprise Software Deal",
            "description": "Potential enterprise customer interested in our platform",
            "status": LeadStatus.NEW,
            "priority": LeadPriority.HIGH,
            "source": LeadSource.WHATSAPP_CAMPAIGN,
            "estimated_value": Decimal("50000.00"),
            "probability": 30,
            "lead_score": 75,
        }
        
        lead = Lead(**lead_data)
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        assert lead.id is not None
        assert lead.title == "Enterprise Software Deal"
        assert lead.is_open is True
        assert lead.is_hot is True
        assert lead.expected_revenue == 15000.0  # 50000 * 0.30

    def test_lead_close_won_lost(self, db: Session):
        """Test closing leads as won or lost."""
        contact = Contact(first_name="Close", email="close@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        lead = Lead(
            contact_id=contact.id,
            title="Test Lead",
            status=LeadStatus.PROPOSAL,
            estimated_value=Decimal("25000.00"),
            probability=60
        )
        db.add(lead)
        db.commit()
        
        # Close as won
        lead.close_won(Decimal("28000.00"))
        db.commit()
        
        assert lead.status == LeadStatus.CLOSED_WON
        assert lead.is_won is True
        assert lead.is_open is False
        assert lead.actual_close_date is not None
        assert lead.estimated_value == Decimal("28000.00")
        assert lead.probability == 100
        
        # Test close lost on another lead
        lead2 = Lead(
            contact_id=contact.id,
            title="Lost Lead",
            status=LeadStatus.NEGOTIATION
        )
        db.add(lead2)
        db.commit()
        
        lead2.close_lost("Chose competitor")
        db.commit()
        
        assert lead2.status == LeadStatus.CLOSED_LOST
        assert lead2.is_lost is True
        assert lead2.probability == 0

    def test_lead_scoring_and_follow_up(self, db: Session):
        """Test lead scoring and follow-up scheduling."""
        contact = Contact(first_name="Score", email="score@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        lead = Lead(
            contact_id=contact.id,
            title="Scoring Test",
            lead_score=50
        )
        db.add(lead)
        db.commit()
        
        # Update score
        lead.update_score(85)
        db.commit()
        
        assert lead.lead_score == 85
        assert lead.is_hot is True
        
        # Schedule follow-up
        follow_up_date = datetime.utcnow() + timedelta(days=7)
        lead.schedule_follow_up(follow_up_date)
        db.commit()
        
        assert lead.next_follow_up == follow_up_date
        
        # Test overdue (simulate past date)
        past_date = datetime.utcnow() - timedelta(days=1)
        lead.next_follow_up = past_date
        db.commit()
        
        assert lead.is_overdue is True

    def test_lead_contact_tracking(self, db: Session):
        """Test lead contact tracking."""
        contact = Contact(first_name="Contact", email="contact@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        lead = Lead(
            contact_id=contact.id,
            title="Contact Test",
            status=LeadStatus.NEW
        )
        db.add(lead)
        db.commit()
        
        # Mark as contacted
        lead.mark_contacted()
        db.commit()
        
        assert lead.last_contact_date is not None
        assert lead.status == LeadStatus.CONTACTED


class TestCRUDOperations:
    """Test CRUD operations for conversations, messages, and leads."""

    def test_conversation_crud_operations(self, db: Session):
        """Test conversation CRUD operations."""
        contact = Contact(first_name="CRUD", email="crud@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        user = User(
            email="support@example.com",
            username="support",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create conversation
        conversation_data = {
            "contact_id": contact.id,
            "subject": "CRUD Test Conversation",
            "priority": "medium",
        }
        
        conversation = conversation_crud.create(db, **conversation_data)
        assert conversation.id is not None
        assert conversation.subject == "CRUD Test Conversation"
        
        # Get conversation
        retrieved = conversation_crud.get(db, conversation.id)
        assert retrieved is not None
        assert retrieved.id == conversation.id
        
        # Assign conversation
        result = conversation_crud.assign_conversation(db, conversation.id, user.id)
        assert result is True
        
        db.refresh(conversation)
        assert conversation.assigned_to == user.id
        
        # Get assigned conversations
        assigned = conversation_crud.get_assigned_conversations(db, user.id)
        assert len(assigned) == 1
        assert assigned[0].id == conversation.id

    def test_message_crud_operations(self, db: Session):
        """Test message CRUD operations."""
        # Setup
        contact = Contact(first_name="Message", email="message@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone = PhoneNumber(contact_id=contact.id, number="+5555555555", country_code="+1")
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        conversation = Conversation(contact_id=contact.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Create message
        message_data = {
            "conversation_id": conversation.id,
            "phone_number_id": phone.id,
            "content": "CRUD test message",
            "direction": MessageDirection.OUTBOUND,
        }
        
        message = message_crud.create(db, **message_data)
        assert message.id is not None
        assert message.content == "CRUD test message"
        
        # Get conversation messages
        messages = message_crud.get_conversation_messages(db, conversation.id)
        assert len(messages) == 1
        assert messages[0].id == message.id
        
        # Mark as sent
        result = message_crud.mark_sent(db, message.id, "whatsapp_123")
        assert result is True
        
        db.refresh(message)
        assert message.status == MessageStatus.SENT
        assert message.whatsapp_message_id == "whatsapp_123"
        
        # Get message by WhatsApp ID
        retrieved = message_crud.get_by_whatsapp_id(db, "whatsapp_123")
        assert retrieved is not None
        assert retrieved.id == message.id

    def test_lead_crud_operations(self, db: Session):
        """Test lead CRUD operations."""
        # Setup
        contact = Contact(first_name="Lead", email="leadcrud@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        user = User(
            email="leadowner@example.com",
            username="leadowner",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create lead
        lead_data = {
            "contact_id": contact.id,
            "title": "CRUD Lead Test",
            "description": "Testing lead CRUD operations",
            "status": LeadStatus.NEW,
            "estimated_value": Decimal("10000.00"),
            "probability": 25,
        }
        
        lead = lead_crud.create(db, **lead_data)
        assert lead.id is not None
        assert lead.title == "CRUD Lead Test"
        
        # Assign lead
        result = lead_crud.assign_lead(db, lead.id, user.id)
        assert result is True
        
        db.refresh(lead)
        assert lead.assigned_to == user.id
        
        # Get assigned leads
        assigned = lead_crud.get_assigned_leads(db, user.id)
        assert len(assigned) == 1
        assert assigned[0].id == lead.id
        
        # Update score
        result = lead_crud.update_score(db, lead.id, 80)
        assert result is True
        
        db.refresh(lead)
        assert lead.lead_score == 80
        
        # Get hot leads
        hot_leads = lead_crud.get_hot_leads(db)
        assert len(hot_leads) == 1
        assert hot_leads[0].id == lead.id
        
        # Close as won
        result = lead_crud.close_won(db, lead.id, Decimal("12000.00"))
        assert result is True
        
        db.refresh(lead)
        assert lead.status == LeadStatus.CLOSED_WON
        assert lead.estimated_value == Decimal("12000.00")