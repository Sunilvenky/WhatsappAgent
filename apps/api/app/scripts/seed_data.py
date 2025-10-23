"""Comprehensive seed data script for WhatsApp marketing system."""

import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session
from apps.api.app.core.database import SessionLocal, engine
from apps.api.app.models import Base
from apps.api.app.crud import (
    contact as contact_crud,
    phone_number as phone_number_crud,
    campaign as campaign_crud,
    conversation as conversation_crud,
    message as message_crud,
    lead as lead_crud
)
from apps.api.app.models.user import User, UserRole
from apps.api.app.models.campaign import CampaignType, CampaignStatus
from apps.api.app.models.conversation import ConversationStatus
from apps.api.app.models.message import MessageDirection, MessageStatus
from apps.api.app.models.lead import LeadStatus, LeadPriority, LeadSource
from apps.api.app.auth.utils import get_password_hash


def create_sample_users(db: Session):
    """Create sample users for different roles."""
    users_data = [
        {
            "email": "admin@whatsappagent.com",
            "username": "admin",
            "full_name": "System Administrator",
            "role": UserRole.ADMIN,
            "is_active": True
        },
        {
            "email": "marketer@whatsappagent.com",
            "username": "sarah_marketing",
            "full_name": "Sarah Johnson",
            "role": UserRole.MARKETER,
            "is_active": True
        },
        {
            "email": "sales1@whatsappagent.com",
            "username": "mike_sales",
            "full_name": "Mike Chen",
            "role": UserRole.SALES,
            "is_active": True
        },
        {
            "email": "sales2@whatsappagent.com",
            "username": "emma_sales",
            "full_name": "Emma Rodriguez",
            "role": UserRole.SALES,
            "is_active": True
        },
        {
            "email": "viewer@whatsappagent.com",
            "username": "john_viewer",
            "full_name": "John Viewer",
            "role": UserRole.VIEWER,
            "is_active": True
        }
    ]
    
    created_users = {}
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            created_users[user_data["role"]] = existing_user
            continue
        
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash("password123"),
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users[user_data["role"]] = user
        print(f"Created user: {user.full_name} ({user.role.value})")
    
    return created_users


def create_sample_contacts(db: Session, count: int = 50):
    """Create sample contacts with phone numbers."""
    companies = [
        "TechCorp Inc", "Global Solutions", "Innovate Ltd", "Digital Dynamics",
        "Future Systems", "Smart Enterprises", "NextGen Co", "Alpha Industries",
        "Beta Technologies", "Gamma Consulting", "Delta Services", "Epsilon Corp",
        "CloudFirst Inc", "DataDriven LLC", "AI Innovations", "Blockchain Bros",
        "CyberSafe Solutions", "AppDev Studios", "WebWorks Inc", "MobileFirst Co"
    ]
    
    first_names = [
        "Alex", "Sarah", "Mike", "Emma", "John", "Lisa", "David", "Anna",
        "Chris", "Maria", "Tom", "Julia", "Sam", "Kate", "Ryan", "Sophie",
        "Mark", "Laura", "Nick", "Amy", "Paul", "Grace", "Luke", "Zoe"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
    ]
    
    created_contacts = []
    
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        company = random.choice(companies)
        
        # 80% opted in, 20% opted out
        opt_in_status = random.random() < 0.8
        
        contact_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '').replace('inc', '').replace('ltd', '').replace('llc', '').replace('co', '')}.com",
            "company": company,
            "job_title": random.choice([
                "CEO", "CTO", "VP Sales", "Marketing Director", "Product Manager",
                "Sales Manager", "Operations Director", "HR Manager", "CFO", "COO"
            ]),
            "opt_in_status": opt_in_status,
            "notes": f"Sample contact from {company}. Interested in digital solutions."
        }
        
        # Check if contact already exists
        existing_contact = contact_crud.get_by_email(db, contact_data["email"])
        if existing_contact:
            created_contacts.append(existing_contact)
            continue
        
        contact = contact_crud.create(db, **contact_data)
        created_contacts.append(contact)
        
        # Add phone number
        country_codes = ["+1", "+44", "+49", "+33", "+61", "+81"]
        country_code = random.choice(country_codes)
        phone_number = f"{country_code}{random.randint(1000000000, 9999999999)}"
        
        phone_data = {
            "contact_id": contact.id,
            "number": phone_number,
            "country_code": country_code,
            "is_whatsapp_verified": random.random() < 0.9,  # 90% verified
            "whatsapp_id": f"{phone_number[1:]}@c.us" if random.random() < 0.9 else None,
            "is_primary": True
        }
        
        phone_number_crud.create(db, **phone_data)
        
        if i % 10 == 0:
            print(f"Created {i+1} contacts...")
    
    print(f"Created {len(created_contacts)} contacts with phone numbers")
    return created_contacts


def create_sample_campaigns(db: Session, users: dict, contacts: list):
    """Create sample campaigns."""
    marketer = users[UserRole.MARKETER]
    
    campaigns_data = [
        {
            "name": "Q4 Product Launch",
            "description": "Announcing our revolutionary AI-powered analytics platform",
            "type": CampaignType.BROADCAST,
            "message_template": "Hi {{first_name}}! 🚀 We're excited to announce our new AI analytics platform. Discover insights like never before: {{product_link}}",
            "created_by": marketer.id,
            "target_criteria": '{"opt_in_status": true, "company_type": "technology"}',
            "personalization_fields": '{"first_name": "contact.first_name", "product_link": "https://example.com/ai-analytics"}',
            "status": CampaignStatus.COMPLETED
        },
        {
            "name": "Holiday Special Offer",
            "description": "50% discount on all premium features for the holidays",
            "type": CampaignType.PROMOTIONAL,
            "message_template": "🎄 Holiday Special! Hi {{first_name}}, get 50% off all premium features. Limited time offer: {{offer_link}}",
            "created_by": marketer.id,
            "target_criteria": '{"opt_in_status": true}',
            "personalization_fields": '{"first_name": "contact.first_name", "offer_link": "https://example.com/holiday-offer"}',
            "status": CampaignStatus.RUNNING
        },
        {
            "name": "Customer Success Stories",
            "description": "Share success stories and case studies",
            "type": CampaignType.NURTURE,
            "message_template": "Hi {{first_name}}! See how {{company_name}} increased their ROI by 300% with our platform: {{case_study_link}}",
            "created_by": marketer.id,
            "target_criteria": '{"opt_in_status": true, "lead_score": ">50"}',
            "personalization_fields": '{"first_name": "contact.first_name", "company_name": "TechCorp", "case_study_link": "https://example.com/case-study"}',
            "status": CampaignStatus.DRAFT
        },
        {
            "name": "Product Demo Invitation",
            "description": "Invite qualified leads to schedule product demos",
            "type": CampaignType.FOLLOW_UP,
            "message_template": "Hi {{first_name}}, based on your interest in {{product_category}}, I'd love to show you a personalized demo. When works best for you?",
            "created_by": marketer.id,
            "target_criteria": '{"opt_in_status": true, "engagement_score": ">70"}',
            "personalization_fields": '{"first_name": "contact.first_name", "product_category": "AI Analytics"}',
            "status": CampaignStatus.PAUSED
        }
    ]
    
    created_campaigns = []
    
    for campaign_data in campaigns_data:
        campaign = campaign_crud.create(db, **campaign_data)
        created_campaigns.append(campaign)
        
        # Add realistic statistics for completed/running campaigns
        if campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.RUNNING]:
            messages_sent = random.randint(20, 100)
            messages_delivered = int(messages_sent * random.uniform(0.85, 0.98))
            messages_read = int(messages_delivered * random.uniform(0.60, 0.85))
            replies_received = int(messages_read * random.uniform(0.05, 0.15))
            
            campaign_crud.update_stats(
                db,
                campaign.id,
                messages_sent=messages_sent,
                messages_delivered=messages_delivered,
                messages_read=messages_read,
                replies_received=replies_received
            )
        
        print(f"Created campaign: {campaign.name}")
    
    return created_campaigns


def create_sample_conversations(db: Session, users: dict, contacts: list, campaigns: list):
    """Create sample conversations with messages."""
    sales_users = [users[UserRole.SALES], users.get(UserRole.SALES)]
    sales_user1 = users[UserRole.SALES]
    
    # Create conversations for a subset of contacts
    sample_contacts = random.sample(contacts, min(15, len(contacts)))
    created_conversations = []
    
    for i, contact in enumerate(sample_contacts):
        if not contact.opt_in_status:
            continue  # Skip opted-out contacts
        
        # Create conversation
        conversation_data = {
            "contact_id": contact.id,
            "subject": f"Discussion with {contact.first_name} {contact.last_name}",
            "assigned_to": sales_user1.id,
            "priority": random.choice(["low", "medium", "high"]),
            "status": random.choice(list(ConversationStatus))
        }
        
        conversation = conversation_crud.create(db, **conversation_data)
        created_conversations.append(conversation)
        
        # Get contact's phone number
        phone_numbers = phone_number_crud.get_by_contact(db, contact.id)
        if not phone_numbers:
            continue
        
        primary_phone = phone_numbers[0]
        
        # Create some messages
        message_count = random.randint(1, 5)
        for msg_idx in range(message_count):
            # Alternate between outbound and inbound messages
            direction = MessageDirection.OUTBOUND if msg_idx % 2 == 0 else MessageDirection.INBOUND
            
            if direction == MessageDirection.OUTBOUND:
                content = random.choice([
                    f"Hi {contact.first_name}, thanks for your interest in our platform!",
                    f"Hello {contact.first_name}, I'd love to schedule a demo for you.",
                    "Based on your company's needs, I think our AI features would be perfect.",
                    "Following up on our previous conversation. Any questions?",
                    "I've prepared a custom proposal for your team."
                ])
            else:
                content = random.choice([
                    "This sounds interesting! Can you tell me more about pricing?",
                    "I'd like to schedule a demo for our team.",
                    "What's the implementation timeline?",
                    "How does this compare to your competitors?",
                    "I need to discuss this with my team first."
                ])
            
            # Select random campaign for outbound messages
            campaign_id = random.choice(campaigns).id if direction == MessageDirection.OUTBOUND else None
            
            message_data = {
                "campaign_id": campaign_id,
                "conversation_id": conversation.id,
                "phone_number_id": primary_phone.id,
                "content": content,
                "direction": direction
            }
            
            message = message_crud.create(db, **message_data)
            
            # Simulate message status progression
            if direction == MessageDirection.OUTBOUND:
                message_crud.mark_sent(db, message.id, f"wa_msg_{message.id}")
                if random.random() < 0.9:  # 90% delivered
                    message_crud.mark_delivered(db, message.id)
                    if random.random() < 0.7:  # 70% read
                        message_crud.mark_read(db, message.id)
        
        # Update conversation with last message info
        has_unread = random.random() < 0.3  # 30% have unread messages
        conversation_crud.update_last_message(
            db, 
            conversation.id, 
            from_contact=has_unread
        )
        
        if i % 5 == 0:
            print(f"Created {i+1} conversations...")
    
    print(f"Created {len(created_conversations)} conversations with messages")
    return created_conversations


def create_sample_leads(db: Session, users: dict, contacts: list, campaigns: list):
    """Create sample leads."""
    sales_users = [users[UserRole.SALES]]
    
    # Create leads for a subset of contacts
    sample_contacts = random.sample(contacts, min(20, len(contacts)))
    created_leads = []
    
    lead_titles = [
        "Enterprise Platform Implementation",
        "AI Analytics Solution",
        "Marketing Automation Setup",
        "Data Integration Project",
        "Custom Development Service",
        "Cloud Migration Consultation",
        "Security Audit Service",
        "Performance Optimization",
        "Training & Support Package",
        "Premium Feature Upgrade"
    ]
    
    for i, contact in enumerate(sample_contacts):
        if not contact.opt_in_status:
            continue
        
        lead_data = {
            "contact_id": contact.id,
            "campaign_id": random.choice(campaigns).id if random.random() < 0.7 else None,
            "assigned_to": random.choice(sales_users).id,
            "title": f"{random.choice(lead_titles)} - {contact.company}",
            "description": f"Potential opportunity with {contact.company}. {contact.first_name} {contact.last_name} has shown interest in our platform.",
            "status": random.choice(list(LeadStatus)),
            "priority": random.choice(list(LeadPriority)),
            "source": random.choice(list(LeadSource)),
            "estimated_value": Decimal(str(random.randint(1000, 50000))),
            "probability": random.randint(10, 90),
            "lead_score": random.randint(30, 100)
        }
        
        lead = lead_crud.create(db, **lead_data)
        created_leads.append(lead)
        
        # Mark some leads as contacted
        if random.random() < 0.6:  # 60% contacted
            lead_crud.mark_contacted(db, lead.id)
        
        # Schedule follow-ups for some leads
        if random.random() < 0.4:  # 40% have follow-ups
            follow_up_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
            lead_crud.schedule_follow_up(db, lead.id, follow_up_date)
        
        # Close some leads as won/lost
        if lead.status == LeadStatus.CLOSED_WON:
            final_value = lead.estimated_value * Decimal(str(random.uniform(0.8, 1.2)))
            lead_crud.close_won(db, lead.id, final_value)
        elif lead.status == LeadStatus.CLOSED_LOST:
            reasons = [
                "Budget constraints",
                "Went with competitor",
                "Project postponed",
                "No longer interested",
                "Internal solution preferred"
            ]
            lead_crud.close_lost(db, lead.id, random.choice(reasons))
        
        if i % 5 == 0:
            print(f"Created {i+1} leads...")
    
    print(f"Created {len(created_leads)} leads")
    return created_leads


def seed_database():
    """Main function to seed the database with sample data."""
    print("Starting database seeding...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create sample data
        print("\n1. Creating sample users...")
        users = create_sample_users(db)
        
        print("\n2. Creating sample contacts...")
        contacts = create_sample_contacts(db, count=50)
        
        print("\n3. Creating sample campaigns...")
        campaigns = create_sample_campaigns(db, users, contacts)
        
        print("\n4. Creating sample conversations...")
        conversations = create_sample_conversations(db, users, contacts, campaigns)
        
        print("\n5. Creating sample leads...")
        leads = create_sample_leads(db, users, contacts, campaigns)
        
        print(f"\n✅ Database seeding completed successfully!")
        print(f"Created:")
        print(f"  - {len(users)} users")
        print(f"  - {len(contacts)} contacts")
        print(f"  - {len(campaigns)} campaigns")
        print(f"  - {len(conversations)} conversations")
        print(f"  - {len(leads)} leads")
        
        print(f"\nLogin credentials:")
        print(f"  Admin: admin@whatsappagent.com / password123")
        print(f"  Marketer: marketer@whatsappagent.com / password123")
        print(f"  Sales: sales1@whatsappagent.com / password123")
        print(f"  Viewer: viewer@whatsappagent.com / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()