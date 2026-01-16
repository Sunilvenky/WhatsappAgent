"""
OTP model for verification codes.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.api.app.core.database import Base


class OTPCode(Base):
    """OTP codes for phone number verification."""
    __tablename__ = "otp_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    phone_number = Column(String(20), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    
    purpose = Column(String(50), nullable=False)  # signup, login, verification, password_reset
    
    # Verification status
    verified_at = Column(DateTime(timezone=True), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Attempts
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=5, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="otp_codes")
    
    __table_args__ = (
        Index('idx_otp_tenant_phone', 'tenant_id', 'phone_number'),
        Index('idx_otp_expires', 'expires_at'),
        Index('idx_otp_verified', 'is_verified'),
    )
