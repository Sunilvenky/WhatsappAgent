"""Script to seed the database with sample WhatsApp marketing data."""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from apps.api.app.core.database import SessionLocal
from apps.api.app.models import (
    Contact, PhoneNumber, Campaign, CampaignStatus, CampaignType,
    Message, MessageStatus, MessageDirection, MessageType,
    Conversation, ConversationStatus, Lead, LeadStatus, LeadSource,
    User, UserRole
)
from apps.api.app.auth.utils import get_password_hash


def create_sample_users(db: Session):
    """Create sample users for testing."""
    users_data = [
        {
            "email": "admin@whatsappagent.com",
            "username": "admin",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "System Administrator",
            "role": UserRole.ADMIN,
        },
        {
            "email": "marketer@whatsappagent.com",
            "username": "sarah_marketer",
            "hashed_password": get_password_hash("marketer123"),
            "full_name": "Sarah Johnson",
            "role": UserRole.MARKETER,
        },
        {
            "email": "sales@whatsappagent.com",
            "username": "mike_sales",
            "hashed_password": get_password_hash("sales123"),
            "full_name": "Mike Thompson",
            "role": UserRole.SALES,
        },
    ]
    
    users = []
    for user_data in users_data:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            users.append(user)
    
    db.commit()
    
    # Refresh to get IDs
    for user in users:
        db.refresh(user)
    
    return db.query(User).all()


def create_sample_contacts(db: Session):
    """Create sample contacts for testing."""
    contacts_data = [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "company": "Tech Solutions Inc",
            "job_title": "CTO",
            "opt_in_status": True,
            "source": "website",
            "tags": '["prospect", "tech"]',
        },
        {
            "first_name": "Emma",
            "last_name": "Johnson",
            "email": "emma.j@startup.co",
            "company": "StartupCo",
            "job_title": "Founder",
            "opt_in_status": True,
            "source": "referral",
            "tags": '["hot-lead", "startup"]',
        },
        {
            "first_name": "Carlos",
            "last_name": "Rodriguez",
            "email": "carlos@retail.com",
            "company": "Retail Solutions",
            "job_title": "Marketing Director",
            "opt_in_status": True,
            "source": "social_media",
            "tags": '["retail", "marketing"]',
        },
        {
            "first_name": "Lisa",
            "last_name": "Chen",
            "email": "lisa.chen@consulting.com",
            "company": "Chen Consulting",
            "job_title": "Principal Consultant",
            "opt_in_status": True,
            "source": "event",
            "tags": '["consultant", "premium"]',
        },
        {
            "first_name": "Ahmed",
            "last_name": "Hassan",
            "email": "ahmed@ecommerce.ae",
            "company": "E-Commerce Hub",
            "job_title": "Operations Manager",
            "opt_in_status": False,
            "opt_out_date": datetime.utcnow() - timedelta(days=30),
            "source": "advertisement",
            "tags": '["ecommerce", "opted-out"]',
        },
    ]
    
    contacts = []
    for contact_data in contacts_data:
        # Check if contact already exists by email
        existing = db.query(Contact).filter(Contact.email == contact_data["email"]).first()
        if not existing:
            contact = Contact(**contact_data)
            db.add(contact)
            contacts.append(contact)
        else:
            contacts.append(existing)
    
    db.commit()
    
    # Refresh to get IDs
    for contact in contacts:
        db.refresh(contact)
    
    return contacts


def create_sample_phone_numbers(db: Session, contacts):
    """Create sample phone numbers for contacts."""
    phone_data = [
        {
            "contact_id": contacts[0].id,
            "number": "+1234567890",
            "country_code": "+1",
            "type": "mobile",
            "is_whatsapp_verified": True,
            "whatsapp_id": "1234567890@c.us",
            "is_primary": True,
        },
        {
            "contact_id": contacts[1].id,
            "number": "+447123456789",
            "country_code": "+44",
            "type": "mobile",
            "is_whatsapp_verified": True,
            "whatsapp_id": "447123456789@c.us",
            "is_primary": True,
        },
        {
            "contact_id": contacts[2].id,
            "number": "+34612345678",
            "country_code": "+34",
            "type": "mobile",
            "is_whatsapp_verified": True,
            "whatsapp_id": "34612345678@c.us",
            "is_primary": True,
        },
        {
            "contact_id": contacts[3].id,
            "number": "+85298765432",
            "country_code": "+852",
            "type": "mobile",
            "is_whatsapp_verified": True,
            "whatsapp_id": "85298765432@c.us",
            "is_primary": True,
        },
        {
            "contact_id": contacts[4].id,
            "number": "+971501234567",
            "country_code": "+971",
            "type": "mobile",
            "is_whatsapp_verified": False,
            "is_primary": True,
        },
    ]
    
    phone_numbers = []
    for phone_info in phone_data:
        # Check if phone number already exists
        existing = db.query(PhoneNumber).filter(PhoneNumber.number == phone_info["number"]).first()
        if not existing:
            phone = PhoneNumber(**phone_info)
            db.add(phone)
            phone_numbers.append(phone)
        else:
            phone_numbers.append(existing)
    
    db.commit()
    
    for phone in phone_numbers:
        db.refresh(phone)
    
    return phone_numbers


def create_sample_campaigns(db: Session, users):
    """Create sample campaigns."""
    marketer = next((u for u in users if u.role == UserRole.MARKETER), users[0])
    
    campaigns_data = [
        {
            "name": "Q4 Product Launch",
            "description": "Announcing our new AI-powered features to existing customers",
            "type": CampaignType.BROADCAST,
            "status": CampaignStatus.COMPLETED,
            "created_by": marketer.id,
            "message_template": "Hi {{first_name}}! 🚀 We're excited to announce our new AI features that will revolutionize your workflow. Check them out: {{product_link}}",
            "target_criteria": {"tags": ["prospect", "customer"], "opt_in_status": True},
            "personalization_fields": {"first_name": "contact.first_name", "product_link": "https://app.example.com/ai-features"},
            "started_at": datetime.utcnow() - timedelta(days=15),
            "ended_at": datetime.utcnow() - timedelta(days=10),
            "total_recipients": 150,
            "messages_sent": 150,
            "messages_delivered": 145,
            "messages_read": 120,
            "replies_received": 25,
            "opt_outs": 2,
        },
        {
            "name": "Holiday Special Offer",
            "description": "Holiday promotion for premium customers",
            "type": CampaignType.BROADCAST,
            "status": CampaignStatus.RUNNING,
            "created_by": marketer.id,
            "message_template": "🎉 Holiday Special: Get 30% off your next purchase! Use code HOLIDAY30. Valid until {{expiry_date}}. Shop now: {{shop_link}}",
            "target_criteria": {"tags": ["premium", "customer"], "opt_in_status": True},
            "personalization_fields": {"expiry_date": "2025-12-31", "shop_link": "https://shop.example.com/holiday"},
            "started_at": datetime.utcnow() - timedelta(days=5),
            "total_recipients": 80,
            "messages_sent": 80,
            "messages_delivered": 78,
            "messages_read": 60,
            "replies_received": 12,
            "opt_outs": 0,
        },
        {
            "name": "Welcome Series - New Signups",
            "description": "Automated welcome series for new subscribers",
            "type": CampaignType.DRIP,
            "status": CampaignStatus.RUNNING,
            "created_by": marketer.id,
            "message_template": "Welcome to WhatsApp Agent, {{first_name}}! 👋 We're here to help you succeed. Here's what you can expect: {{onboarding_link}}",
            "target_criteria": {"source": "website", "opt_in_status": True, "days_since_signup": 0},
            "personalization_fields": {"first_name": "contact.first_name", "onboarding_link": "https://help.example.com/onboarding"},
            "started_at": datetime.utcnow() - timedelta(days=30),
            "total_recipients": 45,
            "messages_sent": 45,
            "messages_delivered": 44,
            "messages_read": 40,
            "replies_received": 8,
            "opt_outs": 1,
        },
    ]
    
    campaigns = []
    for campaign_data in campaigns_data:
        # Check if campaign exists by name
        existing = db.query(Campaign).filter(Campaign.name == campaign_data["name"]).first()
        if not existing:
            campaign = Campaign(**campaign_data)
            db.add(campaign)
            campaigns.append(campaign)
        else:
            campaigns.append(existing)
    
    db.commit()
    
    for campaign in campaigns:
        db.refresh(campaign)
    
    return campaigns


def create_sample_conversations(db: Session, contacts, users):
    """Create sample conversations."""
    sales_user = next((u for u in users if u.role == UserRole.SALES), users[0])
    
    conversations_data = [
        {
            "contact_id": contacts[0].id,
            "assigned_to": sales_user.id,
            "subject": "Product inquiry - Tech Solutions",
            "status": ConversationStatus.ACTIVE,
            "priority": "high",
            "last_message_at": datetime.utcnow() - timedelta(hours=2),
            "last_message_from_contact": True,
            "unread_count": 1,
            "notes": "Customer interested in enterprise features",
        },
        {
            "contact_id": contacts[1].id,
            "assigned_to": sales_user.id,
            "subject": "StartupCo partnership discussion",
            "status": ConversationStatus.ACTIVE,
            "priority": "urgent",
            "last_message_at": datetime.utcnow() - timedelta(minutes=30),
            "last_message_from_contact": False,
            "unread_count": 0,
            "notes": "Potential partnership opportunity",
        },
        {
            "contact_id": contacts[2].id,
            "subject": "Marketing automation inquiry",
            "status": ConversationStatus.CLOSED,
            "priority": "medium",
            "last_message_at": datetime.utcnow() - timedelta(days=5),
            "last_message_from_contact": False,
            "unread_count": 0,
            "closed_at": datetime.utcnow() - timedelta(days=3),
            "notes": "Customer decided to go with competitor",
        },
    ]
    
    conversations = []
    for conv_data in conversations_data:
        # Check if conversation exists for this contact and subject
        existing = db.query(Conversation).filter(
            Conversation.contact_id == conv_data["contact_id"],
            Conversation.subject == conv_data["subject"]
        ).first()
        if not existing:
            conversation = Conversation(**conv_data)
            db.add(conversation)
            conversations.append(conversation)
        else:
            conversations.append(existing)
    
    db.commit()
    
    for conversation in conversations:
        db.refresh(conversation)
    
    return conversations


def create_sample_messages(db: Session, campaigns, conversations, phone_numbers):
    """Create sample messages."""
    messages_data = [
        # Campaign messages
        {
            "campaign_id": campaigns[0].id,
            "conversation_id": conversations[0].id,
            "phone_number_id": phone_numbers[0].id,
            "content": "Hi John! 🚀 We're excited to announce our new AI features that will revolutionize your workflow. Check them out: https://app.example.com/ai-features",
            "message_type": MessageType.TEXT,
            "direction": MessageDirection.OUTBOUND,
            "status": MessageStatus.READ,
            "whatsapp_message_id": "wamid.campaign1_msg1",
            "sent_at": datetime.utcnow() - timedelta(days=15),
            "delivered_at": datetime.utcnow() - timedelta(days=15, hours=1),
            "read_at": datetime.utcnow() - timedelta(days=15, hours=2),
        },
        # Reply to campaign
        {
            "conversation_id": conversations[0].id,
            "phone_number_id": phone_numbers[0].id,
            "content": "This looks great! Can you tell me more about the enterprise pricing?",
            "message_type": MessageType.TEXT,
            "direction": MessageDirection.INBOUND,
            "status": MessageStatus.DELIVERED,
            "whatsapp_message_id": "wamid.reply1_john",
            "sent_at": datetime.utcnow() - timedelta(days=14),
            "delivered_at": datetime.utcnow() - timedelta(days=14),
        },
        # Sales response
        {
            "conversation_id": conversations[0].id,
            "phone_number_id": phone_numbers[0].id,
            "content": "Absolutely! Our enterprise plan includes unlimited AI processing, dedicated support, and custom integrations. Let me schedule a demo for you.",
            "message_type": MessageType.TEXT,
            "direction": MessageDirection.OUTBOUND,
            "status": MessageStatus.READ,
            "whatsapp_message_id": "wamid.sales_response1",
            "sent_at": datetime.utcnow() - timedelta(days=14, hours=-2),
            "delivered_at": datetime.utcnow() - timedelta(days=14, hours=-2, minutes=1),
            "read_at": datetime.utcnow() - timedelta(days=14, hours=-2, minutes=5),
        },
        # Recent message from customer
        {
            "conversation_id": conversations[0].id,
            "phone_number_id": phone_numbers[0].id,
            "content": "Perfect! I'm available tomorrow at 2 PM EST. Should I expect a calendar invite?",
            "message_type": MessageType.TEXT,
            "direction": MessageDirection.INBOUND,
            "status": MessageStatus.DELIVERED,
            "whatsapp_message_id": "wamid.reply2_john",
            "sent_at": datetime.utcnow() - timedelta(hours=2),
            "delivered_at": datetime.utcnow() - timedelta(hours=2),
        },
    ]
    
    messages = []
    for msg_data in messages_data:
        # Check if message exists by whatsapp_message_id
        existing = db.query(Message).filter(Message.whatsapp_message_id == msg_data["whatsapp_message_id"]).first()
        if not existing:
            message = Message(**msg_data)
            db.add(message)
            messages.append(message)
        else:
            messages.append(existing)
    
    db.commit()
    
    for message in messages:
        db.refresh(message)
    
    return messages


def create_sample_leads(db: Session, contacts, campaigns, users):
    """Create sample leads."""
    sales_user = next((u for u in users if u.role == UserRole.SALES), users[0])
    
    leads_data = [
        {
            "contact_id": contacts[0].id,
            "assigned_to": sales_user.id,
            "campaign_id": campaigns[0].id,
            "title": "Enterprise AI Features - Tech Solutions Inc",
            "description": "Interested in enterprise AI features for their development team",
            "status": LeadStatus.QUALIFIED,
            "priority": "high",
            "source": LeadSource.WHATSAPP_CAMPAIGN,
            "estimated_value": Decimal("25000.00"),
            "probability": 70,
            "expected_close_date": datetime.utcnow() + timedelta(days=30),
            "next_follow_up": datetime.utcnow() + timedelta(days=1),
            "lead_score": 85,
            "qualification_notes": "CTO with budget authority, actively evaluating solutions",
            "pain_points": ["manual processes", "scaling issues", "team productivity"],
            "budget_range": "$20k - $30k",
            "decision_maker": True,
            "conversion_source": "AI features announcement",
            "utm_source": "whatsapp",
            "utm_medium": "campaign",
            "utm_campaign": "q4-product-launch",
        },
        {
            "contact_id": contacts[1].id,
            "assigned_to": sales_user.id,
            "title": "Startup Partnership - StartupCo",
            "description": "Potential partnership and reseller opportunity",
            "status": LeadStatus.PROPOSAL,
            "priority": "urgent",
            "source": LeadSource.REFERRAL,
            "estimated_value": Decimal("50000.00"),
            "probability": 60,
            "expected_close_date": datetime.utcnow() + timedelta(days=15),
            "next_follow_up": datetime.utcnow() + timedelta(hours=24),
            "lead_score": 90,
            "qualification_notes": "Founder seeking partnership, high growth potential",
            "pain_points": ["limited resources", "market expansion", "tech stack"],
            "budget_range": "$50k+",
            "decision_maker": True,
            "conversion_source": "founder referral",
        },
        {
            "contact_id": contacts[3].id,
            "assigned_to": sales_user.id,
            "title": "Consulting Services - Chen Consulting",
            "description": "Professional services for client implementations",
            "status": LeadStatus.NEW,
            "priority": "medium",
            "source": LeadSource.EVENT,
            "estimated_value": Decimal("15000.00"),
            "probability": 30,
            "expected_close_date": datetime.utcnow() + timedelta(days=45),
            "next_follow_up": datetime.utcnow() + timedelta(days=7),
            "lead_score": 65,
            "qualification_notes": "Consultant evaluating for client projects",
            "budget_range": "$10k - $20k",
            "decision_maker": True,
        },
    ]
    
    leads = []
    for lead_data in leads_data:
        # Check if lead exists by title
        existing = db.query(Lead).filter(Lead.title == lead_data["title"]).first()
        if not existing:
            lead = Lead(**lead_data)
            db.add(lead)
            leads.append(lead)
        else:
            leads.append(existing)
    
    db.commit()
    
    for lead in leads:
        db.refresh(lead)
    
    return leads


def seed_database():
    """Main function to seed the database with sample data."""
    print("🌱 Starting database seeding...")
    
    db = SessionLocal()
    try:
        # Create sample data
        print("👥 Creating sample users...")
        users = create_sample_users(db)
        print(f"   Created {len(users)} users")
        
        print("📇 Creating sample contacts...")
        contacts = create_sample_contacts(db)
        print(f"   Created {len(contacts)} contacts")
        
        print("📱 Creating sample phone numbers...")
        phone_numbers = create_sample_phone_numbers(db, contacts)
        print(f"   Created {len(phone_numbers)} phone numbers")
        
        print("📢 Creating sample campaigns...")
        campaigns = create_sample_campaigns(db, users)
        print(f"   Created {len(campaigns)} campaigns")
        
        print("💬 Creating sample conversations...")
        conversations = create_sample_conversations(db, contacts, users)
        print(f"   Created {len(conversations)} conversations")
        
        print("📨 Creating sample messages...")
        messages = create_sample_messages(db, campaigns, conversations, phone_numbers)
        print(f"   Created {len(messages)} messages")
        
        print("🎯 Creating sample leads...")
        leads = create_sample_leads(db, contacts, campaigns, users)
        print(f"   Created {len(leads)} leads")
        
        print("✅ Database seeding completed successfully!")
        print("\n📊 Sample data summary:")
        print(f"   - Users: {len(users)}")
        print(f"   - Contacts: {len(contacts)}")
        print(f"   - Phone numbers: {len(phone_numbers)}")
        print(f"   - Campaigns: {len(campaigns)}")
        print(f"   - Conversations: {len(conversations)}")
        print(f"   - Messages: {len(messages)}")
        print(f"   - Leads: {len(leads)}")
        
        print("\n🔐 Sample login credentials:")
        print("   Admin: admin / admin123")
        print("   Marketer: sarah_marketer / marketer123")
        print("   Sales: mike_sales / sales123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()