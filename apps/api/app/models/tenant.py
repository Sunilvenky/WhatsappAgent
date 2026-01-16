"""
Tenant model for multi-tenancy support.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.api.app.core.database import Base


class Tenant(Base):
    """Tenant model representing an organization/workspace."""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=True, unique=True)
    
    # Plan information
    plan = Column(String(50), default="free", nullable=False)  # free, starter, pro, enterprise
    billing_customer_id = Column(String(255), nullable=True)  # Stripe customer ID
    
    # Settings
    settings = Column(JSON, default={}, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="tenant", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="tenant", cascade="all, delete-orphan")
    
    # Existing relationships (will be updated to reference tenants)
    contacts = relationship("Contact", back_populates="tenant")
    campaigns = relationship("Campaign", back_populates="tenant")
    conversations = relationship("Conversation", back_populates="tenant")
    messages = relationship("Message", back_populates="tenant")
    leads = relationship("Lead", back_populates="tenant")
    phone_numbers = relationship("PhoneNumber", back_populates="tenant")
    replies = relationship("Reply", back_populates="tenant")
    unsubscribers = relationship("Unsubscriber", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")
    payment_reminders = relationship("PaymentReminder", back_populates="tenant")
    orders = relationship("Order", back_populates="tenant")
    otp_codes = relationship("OTPCode", back_populates="tenant")
    campaign_steps = relationship("CampaignStep", back_populates="tenant")
    
    __table_args__ = (
        Index('idx_tenant_slug', 'slug'),
        Index('idx_tenant_domain', 'domain'),
        Index('idx_tenant_is_active', 'is_active'),
    )


class TenantUser(Base):
    """User membership in a tenant."""
    __tablename__ = "tenant_users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Role within this tenant (can differ from global role)
    role = Column(String(50), default="member", nullable=False)  # owner, admin, member
    
    # Invitation tracking
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    user = relationship("User", foreign_keys=[user_id])
    invited_by_user = relationship("User", foreign_keys=[invited_by])
    
    __table_args__ = (
        Index('idx_tenant_user_composite', 'tenant_id', 'user_id'),
        Index('idx_tenant_user_active', 'tenant_id', 'is_active'),
    )


class APIKey(Base):
    """API keys for tenant authentication."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Permissions and limits
    permissions = Column(JSON, default=["read", "write"], nullable=False)  # ["read", "write", "delete"]
    rate_limit = Column(Integer, default=1000, nullable=False)  # requests per hour
    
    # Metadata
    description = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="api_keys")
    
    __table_args__ = (
        Index('idx_api_key_tenant', 'tenant_id'),
        Index('idx_api_key_active', 'tenant_id', 'is_active'),
    )


class UsageRecord(Base):
    """Track usage metrics for billing."""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Metrics
    messages_sent = Column(Integer, default=0, nullable=False)
    messages_delivered = Column(Integer, default=0, nullable=False)
    messages_failed = Column(Integer, default=0, nullable=False)
    api_calls = Column(Integer, default=0, nullable=False)
    contacts_count = Column(Integer, default=0, nullable=False)
    conversations_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="usage_records")
    
    __table_args__ = (
        Index('idx_usage_tenant_date', 'tenant_id', 'date'),
    )
