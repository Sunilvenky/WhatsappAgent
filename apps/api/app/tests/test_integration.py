"""Integration tests for the complete WhatsApp marketing system."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from apps.api.app.models import *
from apps.api.app.crud import *
from apps.api.app.auth.utils import get_password_hash


class TestWhatsAppMarketingIntegration:
    """Integration tests for the complete WhatsApp marketing system."""

    def test_complete_campaign_workflow(self, db: Session):
        """Test a complete campaign workflow from creation to analytics."""
        
        # 1. Setup: Create users
        marketer = User(
            email="marketer@integration.com",
            username="marketer_int",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        sales_user = User(
            email="sales@integration.com",
            username="sales_int",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        db.add(marketer)
        db.add(sales_user)
        db.commit()
        db.refresh(marketer)
        db.refresh(sales_user)
        
        # 2. Create contacts with phone numbers
        contacts_data = [
            {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john@company1.com",
                "company": "Company One",
                "opt_in_status": True,
                "phone": "+1234567890"
            },
            {
                "first_name": "Jane",
                "last_name": "Doe", 
                "email": "jane@company2.com",
                "company": "Company Two",
                "opt_in_status": True,
                "phone": "+1987654321"
            },
            {
                "first_name": "Bob",
                "last_name": "Wilson",
                "email": "bob@company3.com",
                "company": "Company Three",
                "opt_in_status": False,  # Opted out
                "phone": "+1555666777"
            }
        ]
        
        contacts = []
        phone_numbers = []
        
        for contact_data in contacts_data:
            phone_number = contact_data.pop("phone")
            contact = contact_crud.create(db, **contact_data)
            contacts.append(contact)
            
            phone = phone_number_crud.create(
                db,
                contact_id=contact.id,
                number=phone_number,
                country_code=phone_number[:2],
                is_whatsapp_verified=True,
                whatsapp_id=f"{phone_number[1:]}@c.us",
                is_primary=True
            )
            phone_numbers.append(phone)
        
        # 3. Create a campaign
        campaign_data = {
            "name": "Product Launch Campaign",
            "description": "Announcing our new AI features",
            "type": CampaignType.BROADCAST,
            "message_template": "Hi {{first_name}}! 🚀 Check out our new AI features: {{product_link}}",
            "created_by": marketer.id,
            "target_criteria": '{"opt_in_status": true}',
            "personalization_fields": '{"first_name": "contact.first_name", "product_link": "https://example.com/ai"}',
        }
        
        campaign = campaign_crud.create(db, **campaign_data)
        assert campaign.id is not None
        assert campaign.status == CampaignStatus.DRAFT
        
        # 4. Start the campaign
        result = campaign_crud.start_campaign(db, campaign.id)
        assert result is True
        
        db.refresh(campaign)
        assert campaign.status == CampaignStatus.RUNNING
        
        # 5. Create conversations and messages for opted-in contacts
        opted_in_contacts = [c for c in contacts if c.opt_in_status]
        conversations = []
        messages = []
        
        for i, contact in enumerate(opted_in_contacts):
            # Create conversation
            conversation = conversation_crud.create(
                db,
                contact_id=contact.id,
                subject=f"Campaign: {campaign.name}",
                status=ConversationStatus.ACTIVE
            )
            conversations.append(conversation)
            
            # Create outbound message
            phone = next(p for p in phone_numbers if p.contact_id == contact.id)
            personalized_content = f"Hi {contact.first_name}! 🚀 Check out our new AI features: https://example.com/ai"
            
            message = message_crud.create(
                db,
                campaign_id=campaign.id,
                conversation_id=conversation.id,
                phone_number_id=phone.id,
                content=personalized_content,
                direction=MessageDirection.OUTBOUND
            )
            messages.append(message)
            
            # Simulate message delivery
            message_crud.mark_sent(db, message.id, f"wa_msg_{i+1}")
            message_crud.mark_delivered(db, message.id)
            if i == 0:  # First contact reads the message
                message_crud.mark_read(db, message.id)
        
        # 6. Simulate customer replies and lead creation
        # John Smith replies positively
        john_conversation = conversations[0]
        john_phone = phone_numbers[0]
        
        # Create reply message
        reply_message = message_crud.create(
            db,
            conversation_id=john_conversation.id,
            phone_number_id=john_phone.id,
            content="This looks amazing! Can you tell me more about pricing?",
            direction=MessageDirection.INBOUND
        )
        
        # Update conversation with new message
        conversation_crud.update_last_message(db, john_conversation.id, from_contact=True)
        
        # Create a lead from this interaction
        lead = lead_crud.create(
            db,
            contact_id=contacts[0].id,
            campaign_id=campaign.id,
            title="AI Features Interest - Company One",
            description="Customer interested in AI features, asking about pricing",
            status=LeadStatus.NEW,
            priority=LeadPriority.HIGH,
            source=LeadSource.WHATSAPP_CAMPAIGN,
            estimated_value=Decimal("15000.00"),
            probability=40,
            lead_score=70
        )
        
        # Assign lead to sales user
        lead_crud.assign_lead(db, lead.id, sales_user.id)
        
        # 7. Sales response
        sales_response = message_crud.create(
            db,
            conversation_id=john_conversation.id,
            phone_number_id=john_phone.id,
            content="Thanks for your interest! Our AI features start at $5,000/month. I'd love to schedule a demo. When works best for you?",
            direction=MessageDirection.OUTBOUND
        )
        message_crud.mark_sent(db, sales_response.id, "wa_sales_1")
        message_crud.mark_delivered(db, sales_response.id)
        
        # Mark lead as contacted
        lead_crud.mark_contacted(db, lead.id)
        
        # 8. Update campaign statistics
        campaign_crud.update_stats(
            db,
            campaign.id,
            messages_sent=2,  # Two opted-in contacts
            messages_delivered=2,
            messages_read=1,
            replies_received=1
        )
        
        # 9. Complete the campaign
        campaign_crud.complete_campaign(db, campaign.id)
        
        # 10. Verify the complete workflow
        db.refresh(campaign)
        assert campaign.status == CampaignStatus.COMPLETED
        assert campaign.messages_sent == 2
        assert campaign.messages_delivered == 2
        assert campaign.messages_read == 1
        assert campaign.replies_received == 1
        assert campaign.delivery_rate == 100.0
        assert campaign.open_rate == 50.0
        assert campaign.reply_rate == 50.0
        
        # Verify lead was created and assigned
        db.refresh(lead)
        assert lead.assigned_to == sales_user.id
        assert lead.status == LeadStatus.CONTACTED
        assert lead.last_contact_date is not None
        
        # Verify conversations
        active_conversations = conversation_crud.get_multi(
            db, 
            status=ConversationStatus.ACTIVE
        )
        assert len(active_conversations) >= 1
        
        # Verify messages
        campaign_messages = message_crud.get_campaign_messages(db, campaign.id)
        assert len(campaign_messages) == 2  # Two outbound messages
        
        conversation_messages = message_crud.get_conversation_messages(
            db, 
            john_conversation.id
        )
        assert len(conversation_messages) == 3  # Outbound, reply, sales response

    def test_lead_lifecycle_management(self, db: Session):
        """Test complete lead lifecycle from creation to close."""
        
        # Setup
        contact = contact_crud.create(
            db,
            first_name="Enterprise",
            last_name="Customer",
            email="enterprise@bigcorp.com",
            company="Big Corp",
            opt_in_status=True
        )
        
        sales_user = User(
            email="enterprise_sales@example.com",
            username="enterprise_sales",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        db.add(sales_user)
        db.commit()
        db.refresh(sales_user)
        
        # Create lead
        lead = lead_crud.create(
            db,
            contact_id=contact.id,
            title="Enterprise Platform Deal",
            description="Large enterprise interested in full platform",
            status=LeadStatus.NEW,
            priority=LeadPriority.URGENT,
            source=LeadSource.REFERRAL,
            estimated_value=Decimal("100000.00"),
            probability=20,
            lead_score=60
        )
        
        # Assign to sales
        lead_crud.assign_lead(db, lead.id, sales_user.id)
        
        # Mark as contacted and update score
        lead_crud.mark_contacted(db, lead.id)
        lead_crud.update_score(db, lead.id, 85)
        
        # Schedule follow-up
        follow_up_date = datetime.utcnow() + timedelta(days=3)
        lead_crud.schedule_follow_up(db, lead.id, follow_up_date)
        
        # Progress through sales stages
        lead_crud.update(db, lead, status=LeadStatus.QUALIFIED, probability=60)
        lead_crud.update(db, lead, status=LeadStatus.PROPOSAL, probability=75)
        lead_crud.update(db, lead, status=LeadStatus.NEGOTIATION, probability=90)
        
        # Close as won
        final_value = Decimal("120000.00")
        lead_crud.close_won(db, lead.id, final_value)
        
        # Verify final state
        db.refresh(lead)
        assert lead.status == LeadStatus.CLOSED_WON
        assert lead.is_won is True
        assert lead.estimated_value == final_value
        assert lead.probability == 100
        assert lead.actual_close_date is not None
        
        # Test lead statistics
        stats = lead_crud.get_lead_stats(db, user_id=sales_user.id)
        assert stats["total"] >= 1
        assert stats["won"] >= 1
        assert stats["won_value"] >= float(final_value)
        assert stats["conversion_rate"] > 0

    def test_conversation_management_workflow(self, db: Session):
        """Test conversation management and assignment workflow."""
        
        # Setup users and contacts
        support_agent1 = User(
            email="support1@example.com",
            username="support1",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        support_agent2 = User(
            email="support2@example.com",
            username="support2",
            hashed_password=get_password_hash("password"),
            role=UserRole.SALES
        )
        db.add(support_agent1)
        db.add(support_agent2)
        db.commit()
        db.refresh(support_agent1)
        db.refresh(support_agent2)
        
        # Create contacts and conversations
        conversations = []
        for i in range(5):
            contact = contact_crud.create(
                db,
                first_name=f"Customer{i+1}",
                email=f"customer{i+1}@example.com",
                opt_in_status=True
            )
            
            conversation = conversation_crud.create(
                db,
                contact_id=contact.id,
                subject=f"Support Request #{i+1}",
                priority="high" if i < 2 else "medium",
                status=ConversationStatus.ACTIVE
            )
            conversations.append(conversation)
        
        # Assign conversations
        for i, conversation in enumerate(conversations):
            if i < 3:
                conversation_crud.assign_conversation(
                    db, 
                    conversation.id, 
                    support_agent1.id
                )
            else:
                conversation_crud.assign_conversation(
                    db, 
                    conversation.id, 
                    support_agent2.id
                )
        
        # Simulate some unread messages
        for i in range(2):
            conversation_crud.update_last_message(
                db, 
                conversations[i].id, 
                from_contact=True
            )
        
        # Test queries
        agent1_conversations = conversation_crud.get_assigned_conversations(
            db, 
            support_agent1.id
        )
        assert len(agent1_conversations) == 3
        
        urgent_conversations = conversation_crud.get_urgent_conversations(
            db, 
            support_agent1.id
        )
        assert len(urgent_conversations) == 2  # First 2 are high priority
        
        unread_conversations = conversation_crud.get_conversations_with_unread(
            db, 
            support_agent1.id
        )
        assert len(unread_conversations) == 2
        
        # Close some conversations
        conversation_crud.close_conversation(db, conversations[0].id)
        conversation_crud.close_conversation(db, conversations[1].id)
        
        # Verify closed conversations
        closed_conversations = conversation_crud.get_multi(
            db,
            assigned_to=support_agent1.id,
            status=ConversationStatus.CLOSED
        )
        assert len(closed_conversations) == 2

    def test_comprehensive_analytics(self, db: Session):
        """Test comprehensive analytics across all entities."""
        
        # Setup test data
        marketer = User(
            email="analytics_marketer@example.com",
            username="analytics_marketer",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(marketer)
        db.commit()
        db.refresh(marketer)
        
        # Create multiple campaigns with different performance
        campaigns = []
        for i in range(3):
            campaign = campaign_crud.create(
                db,
                name=f"Analytics Campaign {i+1}",
                message_template=f"Test message {i+1}",
                created_by=marketer.id,
                type=CampaignType.BROADCAST
            )
            campaigns.append(campaign)
            
            # Simulate different performance levels
            messages_sent = (i+1) * 50
            messages_delivered = int(messages_sent * 0.9)
            messages_read = int(messages_delivered * 0.7)
            replies = int(messages_read * 0.1)
            
            campaign_crud.update_stats(
                db,
                campaign.id,
                messages_sent=messages_sent,
                messages_delivered=messages_delivered,
                messages_read=messages_read,
                replies_received=replies
            )
            
            campaign_crud.complete_campaign(db, campaign.id)
        
        # Test campaign analytics
        completed_campaigns = campaign_crud.get_multi(
            db,
            status=CampaignStatus.COMPLETED,
            created_by=marketer.id
        )
        assert len(completed_campaigns) == 3
        
        total_sent = sum(c.messages_sent for c in completed_campaigns)
        total_delivered = sum(c.messages_delivered for c in completed_campaigns)
        total_read = sum(c.messages_read for c in completed_campaigns)
        total_replies = sum(c.replies_received for c in completed_campaigns)
        
        assert total_sent == 300  # 50 + 100 + 150
        assert total_delivered == 270  # 90% of sent
        assert total_read == 189  # 70% of delivered
        assert total_replies == 18  # 10% of read
        
        # Verify individual campaign performance
        for i, campaign in enumerate(completed_campaigns):
            expected_delivery_rate = 90.0
            expected_open_rate = 70.0
            expected_reply_rate = 10.0
            
            assert abs(campaign.delivery_rate - expected_delivery_rate) < 0.1
            assert abs(campaign.open_rate - expected_open_rate) < 0.1
            assert abs(campaign.reply_rate - expected_reply_rate) < 0.1

    def test_data_integrity_and_relationships(self, db: Session):
        """Test data integrity and relationship constraints."""
        
        # Create a complete data hierarchy
        user = User(
            email="integrity@example.com",
            username="integrity",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        contact = contact_crud.create(
            db,
            first_name="Integrity",
            last_name="Test",
            email="integrity@test.com",
            opt_in_status=True
        )
        
        phone = phone_number_crud.create(
            db,
            contact_id=contact.id,
            number="+1999888777",
            country_code="+1",
            is_whatsapp_verified=True,
            whatsapp_id="1999888777@c.us"
        )
        
        campaign = campaign_crud.create(
            db,
            name="Integrity Test Campaign",
            message_template="Integrity test",
            created_by=user.id
        )
        
        conversation = conversation_crud.create(
            db,
            contact_id=contact.id,
            assigned_to=user.id
        )
        
        message = message_crud.create(
            db,
            campaign_id=campaign.id,
            conversation_id=conversation.id,
            phone_number_id=phone.id,
            content="Test message for integrity"
        )
        
        lead = lead_crud.create(
            db,
            contact_id=contact.id,
            campaign_id=campaign.id,
            assigned_to=user.id,
            title="Integrity Test Lead",
            estimated_value=Decimal("5000.00")
        )
        
        # Verify all relationships exist
        db.refresh(contact)
        db.refresh(phone)
        db.refresh(campaign)
        db.refresh(conversation)
        db.refresh(message)
        db.refresh(lead)
        
        # Test relationship navigation
        assert phone.contact.id == contact.id
        assert message.campaign.id == campaign.id
        assert message.conversation.id == conversation.id
        assert message.phone_number.id == phone.id
        assert lead.contact.id == contact.id
        assert lead.campaign.id == campaign.id
        assert conversation.contact.id == contact.id
        assert conversation.assigned_user.id == user.id
        
        # Test cascading operations
        # Delete contact should cascade to related entities
        contact_id = contact.id
        contact_crud.delete(db, contact_id)
        
        # Verify cascaded deletions
        assert phone_number_crud.get(db, phone.id) is None
        assert conversation_crud.get(db, conversation.id) is None
        assert message_crud.get(db, message.id) is None
        assert lead_crud.get(db, lead.id) is None
        
        # Campaign should still exist (SET NULL relationship)
        assert campaign_crud.get(db, campaign.id) is not None