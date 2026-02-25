"""
Initialize database with default admin user.
"""
from apps.api.app.core.database import SessionLocal, engine, Base
from apps.api.app.models.user import User, UserRole
from apps.api.app.models.tenant import Tenant
from apps.api.app.models.contact import Contact
# Import others to ensure they are registered
from apps.api.app.models.phone_number import PhoneNumber
from apps.api.app.models.campaign import Campaign
from apps.api.app.models.message import Message
from apps.api.app.models.conversation import Conversation
from apps.api.app.models.reply import Reply
from apps.api.app.models.lead import Lead
from apps.api.app.models.unsubscriber import Unsubscriber
from apps.api.app.auth.utils import get_password_hash


def init_db():
    """Initialize database with tables and default admin user."""
    print("Starting init_db script...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Establishing database session...")
    db = SessionLocal()
    try:
        # Check if admin user already exists
        print("Checking for existing admin user...")
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("Admin user already exists")
            return
        
        # Create default admin user
        admin_user = User(
            email="admin@whatsappagent.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Created admin user: {admin_user.username}")
        print("Default credentials: admin / admin123")
        print("⚠️  CHANGE THE DEFAULT PASSWORD IN PRODUCTION!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Main block started")
    init_db()