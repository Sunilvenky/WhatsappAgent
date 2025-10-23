"""Phone number model for storing contact phone numbers."""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class PhoneNumber(Base):
    """
    Phone number model for storing contact phone numbers.
    
    Each contact can have multiple phone numbers with different types
    (mobile, work, home) and WhatsApp verification status.
    """
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    
    # Phone number information
    number = Column(String(20), nullable=False, index=True)  # E.164 format: +1234567890
    country_code = Column(String(5), nullable=False)  # +1, +44, etc.
    type = Column(String(20), default="mobile", nullable=False)  # mobile, work, home
    
    # WhatsApp specific
    is_whatsapp_verified = Column(Boolean, default=False, nullable=False)
    whatsapp_id = Column(String(100), nullable=True, unique=True, index=True)
    
    # Status and metadata
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    contact = relationship("Contact", back_populates="phone_numbers")
    messages = relationship("Message", back_populates="phone_number")

    # Indexes for performance
    __table_args__ = (
        Index("idx_phone_number", "number"),
        Index("idx_phone_contact", "contact_id"),
        Index("idx_phone_whatsapp", "is_whatsapp_verified"),
        Index("idx_phone_primary", "is_primary"),
        Index("idx_phone_whatsapp_id", "whatsapp_id"),
    )

    def __repr__(self):
        return f"<PhoneNumber(id={self.id}, number='{self.number}', contact_id={self.contact_id})>"

    @property
    def formatted_number(self) -> str:
        """Get the formatted phone number."""
        return self.number

    @property
    def is_mobile(self) -> bool:
        """Check if this is a mobile phone number."""
        return self.type == "mobile"

    def mark_as_primary(self) -> None:
        """Mark this phone number as the primary contact number."""
        self.is_primary = True

    def verify_whatsapp(self, whatsapp_id: str = None) -> None:
        """Mark this phone number as WhatsApp verified."""
        self.is_whatsapp_verified = True
        if whatsapp_id:
            self.whatsapp_id = whatsapp_id
        self.verification_date = func.now()