"""CRUD operations for PhoneNumber model."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from apps.api.app.models.phone_number import PhoneNumber


class PhoneNumberCRUD:
    """CRUD operations for PhoneNumber model."""

    def create(self, db: Session, **phone_data) -> PhoneNumber:
        """Create a new phone number."""
        phone = PhoneNumber(**phone_data)
        db.add(phone)
        db.commit()
        db.refresh(phone)
        return phone

    def get(self, db: Session, phone_id: int) -> Optional[PhoneNumber]:
        """Get a phone number by ID."""
        return db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()

    def get_by_number(self, db: Session, number: str) -> Optional[PhoneNumber]:
        """Get a phone number by number."""
        return db.query(PhoneNumber).filter(PhoneNumber.number == number).first()

    def get_by_whatsapp_id(self, db: Session, whatsapp_id: str) -> Optional[PhoneNumber]:
        """Get a phone number by WhatsApp ID."""
        return db.query(PhoneNumber).filter(PhoneNumber.whatsapp_id == whatsapp_id).first()

    def get_by_contact(self, db: Session, contact_id: int) -> List[PhoneNumber]:
        """Get all phone numbers for a contact."""
        return db.query(PhoneNumber).filter(
            PhoneNumber.contact_id == contact_id
        ).all()

    def get_primary_for_contact(self, db: Session, contact_id: int) -> Optional[PhoneNumber]:
        """Get the primary phone number for a contact."""
        return db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.contact_id == contact_id,
                PhoneNumber.is_primary == True,
                PhoneNumber.is_active == True
            )
        ).first()

    def get_whatsapp_for_contact(self, db: Session, contact_id: int) -> Optional[PhoneNumber]:
        """Get the WhatsApp verified phone number for a contact."""
        return db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.contact_id == contact_id,
                PhoneNumber.is_whatsapp_verified == True,
                PhoneNumber.is_active == True
            )
        ).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        contact_id: Optional[int] = None,
        is_whatsapp_verified: Optional[bool] = None
    ) -> List[PhoneNumber]:
        """Get multiple phone numbers with optional filtering."""
        query = db.query(PhoneNumber)
        
        if contact_id:
            query = query.filter(PhoneNumber.contact_id == contact_id)
            
        if is_whatsapp_verified is not None:
            query = query.filter(PhoneNumber.is_whatsapp_verified == is_whatsapp_verified)
        
        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, phone: PhoneNumber, **update_data) -> PhoneNumber:
        """Update a phone number."""
        for field, value in update_data.items():
            if hasattr(phone, field):
                setattr(phone, field, value)
        
        db.commit()
        db.refresh(phone)
        return phone

    def delete(self, db: Session, phone_id: int) -> bool:
        """Delete a phone number."""
        phone = self.get(db, phone_id)
        if phone:
            db.delete(phone)
            db.commit()
            return True
        return False

    def set_as_primary(self, db: Session, phone_id: int) -> bool:
        """Set a phone number as primary for its contact."""
        phone = self.get(db, phone_id)
        if not phone:
            return False
        
        # First, unset any existing primary for this contact
        db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.contact_id == phone.contact_id,
                PhoneNumber.is_primary == True
            )
        ).update({"is_primary": False})
        
        # Set this phone as primary
        phone.is_primary = True
        db.commit()
        return True

    def verify_whatsapp(
        self, 
        db: Session, 
        phone_id: int, 
        whatsapp_id: Optional[str] = None
    ) -> bool:
        """Mark a phone number as WhatsApp verified."""
        phone = self.get(db, phone_id)
        if not phone:
            return False
        
        phone.verify_whatsapp(whatsapp_id)
        db.commit()
        return True

    def get_verified_whatsapp_numbers(self, db: Session, limit: int = 1000) -> List[PhoneNumber]:
        """Get all WhatsApp verified phone numbers."""
        return db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.is_whatsapp_verified == True,
                PhoneNumber.is_active == True
            )
        ).limit(limit).all()

    def count(
        self, 
        db: Session, 
        contact_id: Optional[int] = None,
        is_whatsapp_verified: Optional[bool] = None
    ) -> int:
        """Count phone numbers with optional filtering."""
        query = db.query(PhoneNumber)
        
        if contact_id:
            query = query.filter(PhoneNumber.contact_id == contact_id)
            
        if is_whatsapp_verified is not None:
            query = query.filter(PhoneNumber.is_whatsapp_verified == is_whatsapp_verified)
        
        return query.count()


# Global instance
phone_number_crud = PhoneNumberCRUD()