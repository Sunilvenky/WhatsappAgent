"""
Pydantic schemas for OTP, Payment, Packing, and Drip models.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator


# ==================== OTP SCHEMAS ====================

class OTPCodeBase(BaseModel):
    phone_number: str
    purpose: str  # signup, login, verification, password_reset


class OTPCodeSend(OTPCodeBase):
    """Request to send OTP code"""
    pass


class OTPCodeVerify(BaseModel):
    """Request to verify OTP code"""
    phone_number: str
    code: str
    purpose: str


class OTPCodeResponse(BaseModel):
    id: int
    phone_number: str
    purpose: str
    is_verified: bool
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== PAYMENT SCHEMAS ====================

class InvoiceBase(BaseModel):
    invoice_number: str
    amount: float
    currency: str = "USD"
    due_date: datetime
    description: Optional[str] = None
    items: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    contact_id: Optional[int] = None


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None


class InvoiceResponse(InvoiceBase):
    id: int
    tenant_id: int
    contact_id: Optional[int]
    status: str
    issue_date: datetime
    paid_at: Optional[datetime]
    external_id: Optional[str]
    payment_method: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentReminderBase(BaseModel):
    reminder_type: str  # due, overdue_1day, overdue_7day, custom
    days_before_due: int = 0
    message_template: Optional[str] = None


class PaymentReminderCreate(BaseModel):
    invoice_id: int
    reminder_type: str
    days_before_due: int = 0
    message_template: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None


class PaymentReminderResponse(BaseModel):
    id: int
    tenant_id: int
    invoice_id: int
    reminder_type: str
    days_before_due: int
    scheduled_at: datetime
    sent_at: Optional[datetime]
    is_sent: bool
    retry_count: int

    class Config:
        from_attributes = True


# ==================== PACKING/ORDER SCHEMAS ====================

class OrderItemBase(BaseModel):
    sku: Optional[str] = None
    product_name: str
    quantity: int = 1
    price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    packed_quantity: Optional[int] = None
    is_packed: Optional[bool] = None


class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    packed_quantity: int
    is_packed: bool

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    order_number: str
    total_amount: float
    currency: str = "USD"
    status: str = "pending"
    description: Optional[str] = None
    shipping_address: Optional[str] = None


class OrderCreate(OrderBase):
    contact_id: Optional[int] = None
    external_id: Optional[str] = None
    external_platform: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = []


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None


class OrderResponse(OrderBase):
    id: int
    tenant_id: int
    contact_id: Optional[int]
    external_id: Optional[str]
    external_platform: Optional[str]
    items: List[OrderItemResponse]
    order_date: datetime
    shipped_date: Optional[datetime]
    delivered_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PackingListMessageCreate(BaseModel):
    order_id: int
    message_type: str  # packing_list, shipping_notification, delivery_confirmation


class PackingListMessageResponse(BaseModel):
    id: int
    order_id: int
    message_type: str
    sent_at: Optional[datetime]
    is_sent: bool

    class Config:
        from_attributes = True


# ==================== DRIP CAMPAIGN SCHEMAS ====================

class CampaignStepBase(BaseModel):
    title: str
    description: Optional[str] = None
    step_number: int
    delay_hours: int = 24
    delay_type: str = "hours"
    message_template: str
    template_variables: Optional[Dict[str, Any]] = {}
    conditions: Optional[Dict[str, Any]] = None
    max_retries: int = 3
    is_active: bool = True


class CampaignStepCreate(CampaignStepBase):
    campaign_id: int
    order_index: int


class CampaignStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    delay_hours: Optional[int] = None
    delay_type: Optional[str] = None
    message_template: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class CampaignStepResponse(CampaignStepBase):
    id: int
    tenant_id: int
    campaign_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactCampaignProgressBase(BaseModel):
    contact_id: int
    campaign_id: int


class ContactCampaignProgressCreate(ContactCampaignProgressBase):
    pass


class ContactCampaignProgressUpdate(BaseModel):
    status: Optional[str] = None
    current_step: Optional[int] = None


class ContactCampaignProgressResponse(BaseModel):
    id: int
    tenant_id: int
    contact_id: int
    campaign_id: int
    current_step: int
    status: str
    steps_completed: int
    messages_sent: int
    replies_received: int
    started_at: datetime
    last_step_at: Optional[datetime]
    completed_at: Optional[datetime]
    next_step_scheduled_at: Optional[datetime]
    last_engagement_at: Optional[datetime]

    class Config:
        from_attributes = True
