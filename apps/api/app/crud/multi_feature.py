"""
CRUD operations for OTP, Payment, Packing, and Drip models.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from apps.api.app.models import (
    OTPCode, Invoice, PaymentReminder, Order, OrderItem,
    PackingListMessage, CampaignStep, ContactCampaignProgress
)
import random
import string


class OTPCodeCRUD:
    """CRUD operations for OTP codes."""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate a random OTP code."""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def create(db: Session, tenant_id: int, phone_number: str, purpose: str, 
               expiry_minutes: int = 5) -> tuple[OTPCode, str]:
        """Create a new OTP code."""
        code = OTPCodeCRUD.generate_code()
        
        db_otp = OTPCode(
            tenant_id=tenant_id,
            phone_number=phone_number,
            code=code,
            purpose=purpose,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
        db.add(db_otp)
        db.commit()
        db.refresh(db_otp)
        
        return db_otp, code
    
    @staticmethod
    def verify(db: Session, tenant_id: int, phone_number: str, code: str, purpose: str) -> bool:
        """Verify an OTP code."""
        otp = db.query(OTPCode).filter(
            OTPCode.tenant_id == tenant_id,
            OTPCode.phone_number == phone_number,
            OTPCode.code == code,
            OTPCode.purpose == purpose,
            OTPCode.is_verified == False,
            OTPCode.expires_at > datetime.utcnow()
        ).first()
        
        if not otp:
            return False
        
        # Check max attempts
        if otp.attempts >= otp.max_attempts:
            return False
        
        otp.attempts += 1
        db.commit()
        
        # Mark as verified
        otp.is_verified = True
        otp.verified_at = datetime.utcnow()
        db.commit()
        
        return True
    
    @staticmethod
    def get_active(db: Session, tenant_id: int, phone_number: str, purpose: str) -> Optional[OTPCode]:
        """Get active OTP for phone number."""
        return db.query(OTPCode).filter(
            OTPCode.tenant_id == tenant_id,
            OTPCode.phone_number == phone_number,
            OTPCode.purpose == purpose,
            OTPCode.is_verified == False,
            OTPCode.expires_at > datetime.utcnow()
        ).first()


class InvoiceCRUD:
    """CRUD operations for Invoices."""
    
    @staticmethod
    def create(db: Session, tenant_id: int, invoice_data: dict) -> Invoice:
        """Create a new invoice."""
        db_invoice = Invoice(
            tenant_id=tenant_id,
            **invoice_data
        )
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        return db_invoice
    
    @staticmethod
    def get_by_id(db: Session, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID."""
        return db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    @staticmethod
    def get_by_number(db: Session, tenant_id: int, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by number."""
        return db.query(Invoice).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_number == invoice_number
        ).first()
    
    @staticmethod
    def get_by_tenant(db: Session, tenant_id: int, status: Optional[str] = None, 
                      skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get invoices for a tenant."""
        query = db.query(Invoice).filter(Invoice.tenant_id == tenant_id)
        if status:
            query = query.filter(Invoice.status == status)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_status(db: Session, invoice_id: int, status: str) -> Optional[Invoice]:
        """Update invoice status."""
        invoice = InvoiceCRUD.get_by_id(db, invoice_id)
        if not invoice:
            return None
        
        invoice.status = status
        if status == "paid":
            invoice.paid_at = datetime.utcnow()
        
        db.commit()
        db.refresh(invoice)
        return invoice
    
    @staticmethod
    def get_overdue(db: Session, tenant_id: int) -> List[Invoice]:
        """Get overdue invoices."""
        return db.query(Invoice).filter(
            Invoice.tenant_id == tenant_id,
            Invoice.status == "pending",
            Invoice.due_date < datetime.utcnow()
        ).all()


class PaymentReminderCRUD:
    """CRUD operations for Payment Reminders."""
    
    @staticmethod
    def create(db: Session, tenant_id: int, reminder_data: dict) -> PaymentReminder:
        """Create a new payment reminder."""
        reminder_data['tenant_id'] = tenant_id
        db_reminder = PaymentReminder(**reminder_data)
        db.add(db_reminder)
        db.commit()
        db.refresh(db_reminder)
        return db_reminder
    
    @staticmethod
    def get_pending(db: Session, tenant_id: int) -> List[PaymentReminder]:
        """Get pending reminders to send."""
        return db.query(PaymentReminder).filter(
            PaymentReminder.tenant_id == tenant_id,
            PaymentReminder.is_sent == False,
            PaymentReminder.scheduled_at <= datetime.utcnow()
        ).all()
    
    @staticmethod
    def mark_sent(db: Session, reminder_id: int, message_id: int) -> Optional[PaymentReminder]:
        """Mark reminder as sent."""
        reminder = db.query(PaymentReminder).filter(PaymentReminder.id == reminder_id).first()
        if not reminder:
            return None
        
        reminder.is_sent = True
        reminder.sent_at = datetime.utcnow()
        reminder.message_id = message_id
        db.commit()
        db.refresh(reminder)
        return reminder


class OrderCRUD:
    """CRUD operations for Orders."""
    
    @staticmethod
    def create(db: Session, tenant_id: int, order_data: dict) -> Order:
        """Create a new order."""
        order_data['tenant_id'] = tenant_id
        db_order = Order(**order_data)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID."""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_by_number(db: Session, tenant_id: int, order_number: str) -> Optional[Order]:
        """Get order by order number."""
        return db.query(Order).filter(
            Order.tenant_id == tenant_id,
            Order.order_number == order_number
        ).first()
    
    @staticmethod
    def get_by_tenant(db: Session, tenant_id: int, status: Optional[str] = None) -> List[Order]:
        """Get orders for a tenant."""
        query = db.query(Order).filter(Order.tenant_id == tenant_id)
        if status:
            query = query.filter(Order.status == status)
        return query.all()
    
    @staticmethod
    def update_status(db: Session, order_id: int, status: str) -> Optional[Order]:
        """Update order status."""
        order = OrderCRUD.get_by_id(db, order_id)
        if not order:
            return None
        
        order.status = status
        if status == "shipped":
            order.shipped_date = datetime.utcnow()
        elif status == "delivered":
            order.delivered_date = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        return order


class OrderItemCRUD:
    """CRUD operations for Order Items."""
    
    @staticmethod
    def create(db: Session, order_id: int, item_data: dict) -> OrderItem:
        """Create a new order item."""
        item_data['order_id'] = order_id
        db_item = OrderItem(**item_data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def mark_packed(db: Session, item_id: int, quantity: int) -> Optional[OrderItem]:
        """Mark items as packed."""
        item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        if not item:
            return None
        
        item.packed_quantity = quantity
        if item.packed_quantity >= item.quantity:
            item.is_packed = True
        
        db.commit()
        db.refresh(item)
        return item


class PackingListMessageCRUD:
    """CRUD operations for Packing List Messages."""
    
    @staticmethod
    def create(db: Session, order_id: int, message_type: str) -> PackingListMessage:
        """Create a packing list message record."""
        db_msg = PackingListMessage(
            order_id=order_id,
            message_type=message_type
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg
    
    @staticmethod
    def mark_sent(db: Session, packing_msg_id: int, message_id: int) -> Optional[PackingListMessage]:
        """Mark packing message as sent."""
        msg = db.query(PackingListMessage).filter(PackingListMessage.id == packing_msg_id).first()
        if not msg:
            return None
        
        msg.is_sent = True
        msg.sent_at = datetime.utcnow()
        msg.message_id = message_id
        db.commit()
        db.refresh(msg)
        return msg


class CampaignStepCRUD:
    """CRUD operations for Campaign Steps."""
    
    @staticmethod
    def create(db: Session, tenant_id: int, campaign_id: int, step_data: dict) -> CampaignStep:
        """Create a new campaign step."""
        step_data['tenant_id'] = tenant_id
        step_data['campaign_id'] = campaign_id
        db_step = CampaignStep(**step_data)
        db.add(db_step)
        db.commit()
        db.refresh(db_step)
        return db_step
    
    @staticmethod
    def get_by_campaign(db: Session, campaign_id: int) -> List[CampaignStep]:
        """Get all steps for a campaign."""
        return db.query(CampaignStep).filter(
            CampaignStep.campaign_id == campaign_id,
            CampaignStep.is_active == True
        ).order_by(CampaignStep.step_number).all()
    
    @staticmethod
    def get_step(db: Session, campaign_id: int, step_number: int) -> Optional[CampaignStep]:
        """Get specific step."""
        return db.query(CampaignStep).filter(
            CampaignStep.campaign_id == campaign_id,
            CampaignStep.step_number == step_number
        ).first()


class ContactCampaignProgressCRUD:
    """CRUD operations for Contact Campaign Progress."""
    
    @staticmethod
    def create(db: Session, tenant_id: int, contact_id: int, campaign_id: int) -> ContactCampaignProgress:
        """Create progress record for contact in campaign."""
        db_progress = ContactCampaignProgress(
            tenant_id=tenant_id,
            contact_id=contact_id,
            campaign_id=campaign_id,
            current_step=1,
            status="active"
        )
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress
    
    @staticmethod
    def get_progress(db: Session, contact_id: int, campaign_id: int) -> Optional[ContactCampaignProgress]:
        """Get contact's progress in a campaign."""
        return db.query(ContactCampaignProgress).filter(
            ContactCampaignProgress.contact_id == contact_id,
            ContactCampaignProgress.campaign_id == campaign_id
        ).first()
    
    @staticmethod
    def advance_step(db: Session, progress_id: int) -> Optional[ContactCampaignProgress]:
        """Advance contact to next step."""
        progress = db.query(ContactCampaignProgress).filter(ContactCampaignProgress.id == progress_id).first()
        if not progress:
            return None
        
        progress.current_step += 1
        progress.last_step_at = datetime.utcnow()
        progress.messages_sent += 1
        progress.steps_completed = progress.current_step - 1
        
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def mark_completed(db: Session, progress_id: int) -> Optional[ContactCampaignProgress]:
        """Mark contact as completed the campaign."""
        progress = db.query(ContactCampaignProgress).filter(ContactCampaignProgress.id == progress_id).first()
        if not progress:
            return None
        
        progress.status = "completed"
        progress.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(progress)
        return progress
    
    @staticmethod
    def get_pending_steps(db: Session, tenant_id: int) -> List[ContactCampaignProgress]:
        """Get all pending steps to send."""
        return db.query(ContactCampaignProgress).filter(
            ContactCampaignProgress.tenant_id == tenant_id,
            ContactCampaignProgress.status == "active",
            ContactCampaignProgress.next_step_scheduled_at <= datetime.utcnow()
        ).all()
