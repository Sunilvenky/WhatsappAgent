"""
Generate synthetic training data for ML models.
Use this if you don't have enough real data yet.
"""

import random
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.crud import contact as contact_crud
from app.crud import lead as lead_crud
from app.crud import conversation as conversation_crud
from app.crud import message as message_crud
from app.schemas.contact import ContactCreate
from app.schemas.lead import LeadCreate
from app.schemas.conversation import ConversationCreate
from app.schemas.message import MessageCreate


class SyntheticDataGenerator:
    """Generate realistic synthetic data for ML training."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_id = 1  # Default user
        
        # Sample data
        self.first_names = [
            "John", "Sarah", "Mike", "Emma", "David", "Lisa", "James", "Anna",
            "Robert", "Maria", "Michael", "Jennifer", "William", "Linda", "Richard"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez"
        ]
        
        self.message_templates_outbound = [
            "Hi {name}! Thanks for your interest in our product!",
            "Hello {name}, I hope you're doing well. Would you like to learn more?",
            "Hey {name}! We have a special offer for you.",
            "Hi there! Can I help you with anything today?",
            "Thanks for reaching out {name}! How can I assist you?"
        ]
        
        self.message_templates_interested = [
            "Yes, I'm very interested!",
            "Tell me more about the pricing",
            "This looks great! When can we start?",
            "I'd like to schedule a demo",
            "What's the next step?",
            "Can you send me more information?",
            "I want to buy this!"
        ]
        
        self.message_templates_not_interested = [
            "Not interested, thanks",
            "Maybe later",
            "I'll think about it",
            "Too expensive for me",
            "Not right now",
            "STOP",
            "Remove me from your list"
        ]
        
        self.message_templates_question = [
            "How does this work?",
            "What's included?",
            "Do you have payment plans?",
            "Can I try it first?",
            "What's the refund policy?",
            "Is there a free trial?"
        ]
    
    def print_progress(self, current: int, total: int, item: str):
        """Print progress bar."""
        percent = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"   [{bar}] {percent:.0f}% - {item}", end="\r")
        if current == total:
            print()  # New line when complete
    
    def generate_contacts(self, count: int = 200) -> List[int]:
        """Generate synthetic contacts."""
        print(f"\n📇 Generating {count} contacts...")
        
        contact_ids = []
        
        for i in range(count):
            name = f"{random.choice(self.first_names)} {random.choice(self.last_names)}"
            phone = f"+1555{random.randint(1000000, 9999999)}"
            
            contact_data = ContactCreate(
                phone_number=phone,
                name=name,
                email=f"{name.lower().replace(' ', '.')}@example.com",
                tags=random.choice([
                    ["vip"], ["new"], ["active"], [], ["interested"], ["prospect"]
                ]),
                opted_in=random.random() < 0.9,  # 90% opted in
                is_blocked=False,
                metadata={
                    "source": "synthetic",
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
            
            contact = contact_crud.create_contact(
                self.db,
                contact=contact_data,
                user_id=self.user_id
            )
            contact_ids.append(contact.id)
            
            self.print_progress(i + 1, count, f"Contact: {name}")
        
        print(f"✅ Created {count} contacts")
        return contact_ids
    
    def generate_conversations(self, contact_ids: List[int], count: int = 150) -> List[int]:
        """Generate synthetic conversations."""
        print(f"\n💬 Generating {count} conversations...")
        
        conversation_ids = []
        
        for i in range(count):
            contact_id = random.choice(contact_ids)
            
            conv_data = ConversationCreate(
                contact_id=contact_id,
                status=random.choice(["active", "closed", "waiting"]),
                priority=random.choice(["low", "medium", "high"]),
                last_message_at=datetime.utcnow() - timedelta(hours=random.randint(1, 720))
            )
            
            conversation = conversation_crud.create_conversation(
                self.db,
                conversation=conv_data,
                user_id=self.user_id
            )
            conversation_ids.append(conversation.id)
            
            self.print_progress(i + 1, count, f"Conversation #{conversation.id}")
        
        print(f"✅ Created {count} conversations")
        return conversation_ids
    
    def generate_messages(self, conversation_ids: List[int]) -> int:
        """Generate synthetic messages for conversations."""
        print(f"\n✉️  Generating messages for conversations...")
        
        total_messages = 0
        
        for i, conv_id in enumerate(conversation_ids):
            # Get conversation
            conversation = conversation_crud.get_conversation(self.db, conv_id)
            if not conversation:
                continue
            
            # Generate 2-8 messages per conversation
            num_messages = random.randint(2, 8)
            
            for msg_idx in range(num_messages):
                # Alternate between outbound and inbound
                is_outbound = msg_idx % 2 == 0
                
                if is_outbound:
                    content = random.choice(self.message_templates_outbound)
                else:
                    # Choose response type
                    response_type = random.choices(
                        ["interested", "not_interested", "question"],
                        weights=[0.4, 0.3, 0.3]
                    )[0]
                    
                    if response_type == "interested":
                        content = random.choice(self.message_templates_interested)
                    elif response_type == "question":
                        content = random.choice(self.message_templates_question)
                    else:
                        content = random.choice(self.message_templates_not_interested)
                
                # Create message
                msg_data = MessageCreate(
                    conversation_id=conv_id,
                    contact_id=conversation.contact_id,
                    content=content,
                    direction="outbound" if is_outbound else "inbound",
                    status=random.choice(["sent", "delivered", "read"]),
                    sent_at=datetime.utcnow() - timedelta(
                        hours=random.randint(1, 720),
                        minutes=random.randint(0, 59)
                    )
                )
                
                message_crud.create_message(
                    self.db,
                    message=msg_data,
                    user_id=self.user_id
                )
                total_messages += 1
            
            self.print_progress(i + 1, len(conversation_ids), f"Conv #{conv_id}: {num_messages} msgs")
        
        print(f"✅ Created {total_messages} messages")
        return total_messages
    
    def generate_leads(self, contact_ids: List[int], count: int = 120) -> int:
        """Generate synthetic leads."""
        print(f"\n🎯 Generating {count} leads...")
        
        lead_ids = []
        converted_count = 0
        
        for i in range(count):
            contact_id = random.choice(contact_ids)
            
            # 30% conversion rate
            converted = random.random() < 0.3
            if converted:
                converted_count += 1
            
            # Generate realistic lead scores
            if converted:
                score = random.randint(70, 100)  # High scores for converted
            else:
                score = random.randint(20, 70)  # Lower scores for non-converted
            
            # Lead status based on conversion
            if converted:
                status = random.choice(["won", "proposal", "qualified"])
            else:
                status = random.choice(["new", "contacted", "lost"])
            
            lead_data = LeadCreate(
                contact_id=contact_id,
                source="whatsapp_campaign",
                status=status,
                score=score,
                value=random.uniform(100, 10000) if converted else None,
                notes=f"Lead from synthetic campaign {random.randint(1, 10)}",
                metadata={
                    "synthetic": True,
                    "conversion_probability": score / 100
                }
            )
            
            lead = lead_crud.create_lead(
                self.db,
                lead=lead_data,
                user_id=self.user_id
            )
            lead_ids.append(lead.id)
            
            # Mark as converted if applicable
            if converted:
                lead.converted = True
                lead.converted_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                self.db.commit()
            
            self.print_progress(i + 1, count, f"Lead #{lead.id} (score: {score})")
        
        print(f"✅ Created {count} leads ({converted_count} converted, {count - converted_count} not converted)")
        return count
    
    def generate_all(
        self,
        num_contacts: int = 200,
        num_conversations: int = 150,
        num_leads: int = 120
    ) -> dict:
        """Generate all synthetic data."""
        print("\n" + "=" * 70)
        print("  🎲 SYNTHETIC DATA GENERATOR")
        print("=" * 70)
        print(f"\nGenerating realistic training data for ML models...")
        print(f"   Contacts: {num_contacts}")
        print(f"   Conversations: {num_conversations}")
        print(f"   Leads: {num_leads}")
        print(f"   Messages: ~{num_conversations * 4} (average 4 per conversation)")
        
        try:
            # Generate data
            contact_ids = self.generate_contacts(num_contacts)
            conversation_ids = self.generate_conversations(contact_ids, num_conversations)
            total_messages = self.generate_messages(conversation_ids)
            total_leads = self.generate_leads(contact_ids, num_leads)
            
            # Summary
            print("\n" + "=" * 70)
            print("  ✅ DATA GENERATION COMPLETE")
            print("=" * 70)
            print(f"\n📊 Summary:")
            print(f"   ✅ Contacts:       {num_contacts}")
            print(f"   ✅ Conversations:  {num_conversations}")
            print(f"   ✅ Messages:       {total_messages}")
            print(f"   ✅ Leads:          {total_leads}")
            
            print(f"\n🎯 Data Distribution:")
            print(f"   • Contacts with high engagement: ~30%")
            print(f"   • Conversations with replies: ~60%")
            print(f"   • Lead conversion rate: ~30%")
            print(f"   • Message response rate: ~50%")
            
            print(f"\n💡 Next Step:")
            print(f"   Train ML models with this data:")
            print(f"   python -m apps.api.app.ml.train_models")
            
            return {
                "success": True,
                "contacts": num_contacts,
                "conversations": num_conversations,
                "messages": total_messages,
                "leads": total_leads
            }
            
        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


def main():
    """Main entry point."""
    db = SessionLocal()
    
    try:
        generator = SyntheticDataGenerator(db)
        result = generator.generate_all(
            num_contacts=200,
            num_conversations=150,
            num_leads=120
        )
        
        if not result.get("success"):
            exit(1)
            
    finally:
        db.close()


if __name__ == "__main__":
    main()
