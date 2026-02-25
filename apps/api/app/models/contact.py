"""Contact model for storing customer contact information."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.api.app.core.database import Base


class Contact(Base):
    """
    Contact model for storing customer contact information.
    
    A contact represents a potential or existing customer with their
    personal information and contact preferences.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True, index=True)
    
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    company = Column(String(255), nullable=True, index=True)
    job_title = Column(String(255), nullable=True)
    
    # WhatsApp preferences
    opt_in_status = Column(Boolean, default=True, nullable=False)
    opt_in_date = Column(DateTime(timezone=True), nullable=True)
    opt_out_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    tags = Column(Text, nullable=True)  # JSON string for flexible tagging
    notes = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)  # Where contact came from
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_contacted = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="contacts")
    phone_numbers = relationship("PhoneNumber", back_populates="contact", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="contact", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="contact", cascade="all, delete-orphan")
    unsubscribers = relationship("Unsubscriber", back_populates="contact", cascade="all, delete-orphan")
    campaign_progress = relationship("ContactCampaignProgress", back_populates="contact", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="contact", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="contact", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index("idx_contact_name", "first_name", "last_name"),
        Index("idx_contact_company", "company"),
        Index("idx_contact_opt_status", "opt_in_status"),
        Index("idx_contact_created", "created_at"),
        Index("idx_contact_last_contacted", "last_contacted"),
    )

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.first_name} {self.last_name}', email='{self.email}')>"

    @property
    def full_name(self) -> str:
        """Get the full name of the contact."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def is_opted_in(self) -> bool:
        """Check if the contact is opted in for WhatsApp messaging."""
        return self.opt_in_status

    def opt_out(self) -> None:
        """Opt out the contact from WhatsApp messaging."""
        self.opt_in_status = False
        self.opt_out_date = datetime.utcnow()

    def opt_in(self) -> None:
        """Opt in the contact for WhatsApp messaging."""
        self.opt_in_status = True
        self.opt_in_date = datetime.utcnow()
        self.opt_out_date = None