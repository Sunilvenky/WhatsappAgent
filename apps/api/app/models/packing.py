"""
Order and packing list models for e-commerce integration.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.api.app.core.database import Base


class Order(Base):
    """Orders for e-commerce integration."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, confirmed, shipped, delivered, cancelled
    
    # Amount
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # External reference (from Shopify, WooCommerce, etc.)
    external_id = Column(String(255), nullable=True, index=True)
    external_platform = Column(String(50), nullable=True)  # shopify, woocommerce, custom
    
    # Details
    description = Column(String(500), nullable=True)
    shipping_address = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)  # JSON
    
    # Dates
    order_date = Column(DateTime(timezone=True), nullable=False)
    shipped_date = Column(DateTime(timezone=True), nullable=True)
    delivered_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="orders")
    contact = relationship("Contact", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    packing_list_messages = relationship("PackingListMessage", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_order_tenant', 'tenant_id'),
        Index('idx_order_contact', 'contact_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_external', 'external_id'),
    )


class OrderItem(Base):
    """Individual items in an order."""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    sku = Column(String(100), nullable=True)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    packed_quantity = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)
    
    # Status
    is_packed = Column(Boolean, default=False, nullable=False)
    
    # Details
    notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    
    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
    )


class PackingListMessage(Base):
    """Packing list messages sent for orders."""
    __tablename__ = "packing_list_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Message content
    message_type = Column(String(50), nullable=False)  # packing_list, shipping_notification, delivery_confirmation
    
    # Status
    sent_at = Column(DateTime(timezone=True), nullable=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="packing_list_messages")
    message = relationship("Message")
    
    __table_args__ = (
        Index('idx_packing_order', 'order_id'),
        Index('idx_packing_sent', 'is_sent'),
    )
