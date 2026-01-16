"""
Payment and invoice models for billing and reminders.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.api.app.core.database import Base


class Invoice(Base):
    """Invoices for payment tracking."""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Payment status
    status = Column(String(50), nullable=False, default="pending")  # pending, sent, paid, overdue, cancelled
    
    # Dates
    issue_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment reference
    external_id = Column(String(255), nullable=True)  # Stripe invoice ID
    payment_method = Column(String(50), nullable=True)  # stripe, manual, etc.
    
    # Description
    description = Column(String(500), nullable=True)
    items = Column(String(500), nullable=True)  # JSON-like description of line items
    
    # Additional metadata
    notes = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="invoices")
    contact = relationship("Contact", back_populates="invoices")
    payment_reminders = relationship("PaymentReminder", back_populates="invoice", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_invoice_tenant', 'tenant_id'),
        Index('idx_invoice_contact', 'contact_id'),
        Index('idx_invoice_status', 'status'),
        Index('idx_invoice_due_date', 'due_date'),
    )


class PaymentReminder(Base):
    """Scheduled payment reminders to be sent via WhatsApp."""
    __tablename__ = "payment_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    
    # Reminder configuration
    reminder_type = Column(String(50), nullable=False)  # due, overdue_1day, overdue_7day, custom
    days_before_due = Column(Integer, default=0, nullable=False)  # 0 = on due date
    
    # Template
    message_template = Column(String(500), nullable=True)
    template_variables = Column(String(500), nullable=True)  # JSON
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    
    # Message reference
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Retry logic
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="payment_reminders")
    invoice = relationship("Invoice", back_populates="payment_reminders")
    message = relationship("Message")
    
    __table_args__ = (
        Index('idx_reminder_tenant', 'tenant_id'),
        Index('idx_reminder_invoice', 'invoice_id'),
        Index('idx_reminder_scheduled', 'scheduled_at'),
        Index('idx_reminder_sent', 'is_sent'),
    )
