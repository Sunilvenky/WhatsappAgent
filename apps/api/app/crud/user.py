"""
CRUD operations for User model.
"""
from typing import Optional
from sqlalchemy.orm import Session
from apps.api.app.models.user import User
from apps.api.app.schemas.auth import UserCreate, UserUpdate
from apps.api.app.auth.utils import get_password_hash, verify_password


class UserCRUD:
    """CRUD operations for User model."""

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username or email and password."""
        # Try fetching by username first
        user = self.get_user_by_username(db, username)
        
        # If not found, try fetching by email (case-insensitive)
        if not user:
            user = self.get_user_by_email(db, username.lower())
            
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update a user."""
        user = self.get_user(db, user_id)
        if not user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user


# Global instance
user_crud = UserCRUD()

# Keep the old function names for backwards compatibility
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return user_crud.get_user(db, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return user_crud.get_user_by_email(db, email)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return user_crud.get_user_by_username(db, username)

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    return user_crud.create_user(db, user)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    return user_crud.authenticate_user(db, username, password)

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update a user."""
    return user_crud.update_user(db, user_id, user_update)