"""
OTP, Payment, Packing, and Drip campaign API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from apps.api.app.core.database import get_db
from apps.api.app.auth.dependencies import get_current_active_user
from apps.api.app.auth.tenant_dependencies import get_current_tenant
from apps.api.app.models import User, Tenant
from apps.api.app.schemas.multi_feature import (
    OTPCodeSend, OTPCodeVerify, OTPCodeResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    PaymentReminderCreate, PaymentReminderResponse,
    OrderCreate, OrderUpdate, OrderResponse, OrderItemUpdate,
    CampaignStepCreate, CampaignStepUpdate, CampaignStepResponse,
    ContactCampaignProgressResponse
)
from apps.api.app.crud.multi_feature import (
    OTPCodeCRUD, InvoiceCRUD, PaymentReminderCRUD,
    OrderCRUD, OrderItemCRUD, PackingListMessageCRUD,
    CampaignStepCRUD, ContactCampaignProgressCRUD
)

router = APIRouter(prefix="/api/v1", tags=["Features"])


# ==================== OTP ENDPOINTS ====================

@router.post("/otp/send", response_model=OTPCodeResponse)
async def send_otp(
    otp_request: OTPCodeSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Send an OTP code to a phone number.
    """
    # Check if OTP already exists and is pending
    existing = OTPCodeCRUD.get_active(db, current_tenant.id, otp_request.phone_number, otp_request.purpose)
    if existing:
        # Could throw error or allow resend - implement based on requirement
        pass
    
    db_otp, code = OTPCodeCRUD.create(db, current_tenant.id, otp_request.phone_number, otp_request.purpose)
    
    # TODO: Send OTP via WhatsApp or SMS
    # For now, log it (in production, use SMS/WhatsApp provider)
    print(f"OTP Code: {code} for {otp_request.phone_number}")
    
    return db_otp


@router.post("/otp/verify", response_model=dict)
async def verify_otp(
    otp_verify: OTPCodeVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Verify an OTP code.
    """
    verified = OTPCodeCRUD.verify(db, current_tenant.id, otp_verify.phone_number, otp_verify.code, otp_verify.purpose)
    
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code or code has expired"
        )
    
    return {"success": True, "message": "OTP verified successfully"}


# ==================== INVOICE & PAYMENT ENDPOINTS ====================

@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Create a new invoice."""
    invoice_data = invoice.dict()
    invoice_data['tenant_id'] = current_tenant.id
    invoice_data['status'] = 'pending'
    
    db_invoice = InvoiceCRUD.create(db, current_tenant.id, invoice_data)
    return db_invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get invoice details."""
    invoice = InvoiceCRUD.get_by_id(db, invoice_id)
    if not invoice or invoice.tenant_id != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """List invoices for the current tenant."""
    invoices = InvoiceCRUD.get_by_tenant(db, current_tenant.id, status=status)
    return invoices


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Update invoice status or details."""
    invoice = InvoiceCRUD.get_by_id(db, invoice_id)
    if not invoice or invoice.tenant_id != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice_update.status:
        invoice = InvoiceCRUD.update_status(db, invoice_id, invoice_update.status)
    
    return invoice


@router.post("/invoices/{invoice_id}/reminders", response_model=PaymentReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_reminder(
    invoice_id: int,
    reminder: PaymentReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Create a payment reminder for an invoice."""
    invoice = InvoiceCRUD.get_by_id(db, invoice_id)
    if not invoice or invoice.tenant_id != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    reminder_data = reminder.dict()
    db_reminder = PaymentReminderCRUD.create(db, current_tenant.id, reminder_data)
    return db_reminder


# ==================== ORDER & PACKING ENDPOINTS ====================

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Create a new order."""
    order_data = order.dict(exclude={'items'})
    order_data['tenant_id'] = current_tenant.id
    order_data['order_date'] = order_data.get('order_date') or __import__('datetime').datetime.utcnow()
    
    db_order = OrderCRUD.create(db, current_tenant.id, order_data)
    
    # Add items
    if order.items:
        for item in order.items:
            OrderItemCRUD.create(db, db_order.id, item.dict())
    
    return db_order


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get order details."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order or order.tenant_id != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Update order status."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order or order.tenant_id != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order_update.status:
        order = OrderCRUD.update_status(db, order_id, order_update.status)
    
    return order


@router.put("/orders/{order_id}/items/{item_id}/pack", response_model=dict)
async def mark_item_packed(
    order_id: int,
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Mark order item as packed."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order or order.tenant_id != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    item = OrderItemCRUD.mark_packed(db, item_id, quantity)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    
    return {"success": True, "is_packed": item.is_packed}


# ==================== DRIP CAMPAIGN ENDPOINTS ====================

@router.post("/campaigns/{campaign_id}/steps", response_model=CampaignStepResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign_step(
    campaign_id: int,
    step: CampaignStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Create a step in a drip campaign."""
    step_data = step.dict()
    step_data.pop('campaign_id')  # Remove as we set it explicitly
    
    db_step = CampaignStepCRUD.create(db, current_tenant.id, campaign_id, step_data)
    return db_step


@router.get("/campaigns/{campaign_id}/steps", response_model=List[CampaignStepResponse])
async def get_campaign_steps(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get all steps for a campaign."""
    steps = CampaignStepCRUD.get_by_campaign(db, campaign_id)
    return steps


@router.put("/campaigns/{campaign_id}/steps/{step_id}", response_model=CampaignStepResponse)
async def update_campaign_step(
    campaign_id: int,
    step_id: int,
    step_update: CampaignStepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Update a campaign step."""
    step = db.query(db.query(type(db.query(type(None)))).__self__.__class__).filter_by(id=step_id).first()
    # Note: Would need proper implementation of update
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Coming soon")


@router.post("/contacts/{contact_id}/campaign/{campaign_id}/enroll", response_model=ContactCampaignProgressResponse, status_code=status.HTTP_201_CREATED)
async def enroll_contact_in_drip(
    contact_id: int,
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Enroll a contact in a drip campaign."""
    # Check if already enrolled
    existing = ContactCampaignProgressCRUD.get_progress(db, contact_id, campaign_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact already enrolled in this campaign"
        )
    
    progress = ContactCampaignProgressCRUD.create(db, current_tenant.id, contact_id, campaign_id)
    return progress


@router.get("/contacts/{contact_id}/campaigns/{campaign_id}/progress", response_model=ContactCampaignProgressResponse)
async def get_campaign_progress(
    contact_id: int,
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get contact's progress in a drip campaign."""
    progress = ContactCampaignProgressCRUD.get_progress(db, contact_id, campaign_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    return progress
