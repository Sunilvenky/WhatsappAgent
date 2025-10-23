"""
User model with role-based access control.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.api.app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    MARKETER = "marketer"
    SALES = "sales"


class User(Base):
    """User model with authentication and role management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.SALES, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    campaigns = relationship("Campaign", back_populates="creator")
    assigned_conversations = relationship("Conversation", back_populates="assigned_user")
    assigned_leads = relationship("Lead", back_populates="assigned_user")
    processed_replies = relationship("Reply", back_populates="processed_by_user")
    processed_unsubscribers = relationship("Unsubscriber", back_populates="processed_by_user")