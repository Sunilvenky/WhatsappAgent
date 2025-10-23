"""
Initialize database with default admin user.
"""
from apps.api.app.core.database import SessionLocal, engine
from apps.api.app.models.user import User, UserRole
from apps.api.app.auth.utils import get_password_hash
from apps.api.app.core.database import Base


def init_db():
    """Initialize database with tables and default admin user."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin user already exists
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
    init_db()