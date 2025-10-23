"""CRUD operations for Contact model."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from apps.api.app.models.contact import Contact
from apps.api.app.models.phone_number import PhoneNumber


class ContactCRUD:
    """CRUD operations for Contact model."""

    def create(self, db: Session, **contact_data) -> Contact:
        """Create a new contact."""
        contact = Contact(**contact_data)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact

    def get(self, db: Session, contact_id: int) -> Optional[Contact]:
        """Get a contact by ID."""
        return db.query(Contact).filter(Contact.id == contact_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Contact]:
        """Get a contact by email."""
        return db.query(Contact).filter(Contact.email == email).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        company: Optional[str] = None,
        opt_in_status: Optional[bool] = None
    ) -> List[Contact]:
        """Get multiple contacts with optional filtering."""
        query = db.query(Contact)
        
        if search:
            search_filter = or_(
                Contact.first_name.ilike(f"%{search}%"),
                Contact.last_name.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
                Contact.company.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if company:
            query = query.filter(Contact.company.ilike(f"%{company}%"))
            
        if opt_in_status is not None:
            query = query.filter(Contact.opt_in_status == opt_in_status)
        
        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, contact: Contact, **update_data) -> Contact:
        """Update a contact."""
        for field, value in update_data.items():
            if hasattr(contact, field):
                setattr(contact, field, value)
        
        db.commit()
        db.refresh(contact)
        return contact

    def delete(self, db: Session, contact_id: int) -> bool:
        """Delete a contact."""
        contact = self.get(db, contact_id)
        if contact:
            db.delete(contact)
            db.commit()
            return True
        return False

    def get_opted_in_contacts(self, db: Session, limit: int = 1000) -> List[Contact]:
        """Get all contacts that are opted in for messaging."""
        return db.query(Contact).filter(
            Contact.opt_in_status == True
        ).limit(limit).all()

    def get_contacts_with_whatsapp(self, db: Session, limit: int = 1000) -> List[Contact]:
        """Get contacts that have verified WhatsApp numbers."""
        return db.query(Contact).join(PhoneNumber).filter(
            and_(
                Contact.opt_in_status == True,
                PhoneNumber.is_whatsapp_verified == True,
                PhoneNumber.is_active == True
            )
        ).limit(limit).all()

    def search_contacts(
        self, 
        db: Session, 
        query: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Contact]:
        """Search contacts by name, email, or company."""
        search_filter = or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%"),
            Contact.company.ilike(f"%{query}%")
        )
        
        return db.query(Contact).filter(search_filter).offset(skip).limit(limit).all()

    def count(self, db: Session, opt_in_status: Optional[bool] = None) -> int:
        """Count contacts, optionally filtered by opt-in status."""
        query = db.query(Contact)
        if opt_in_status is not None:
            query = query.filter(Contact.opt_in_status == opt_in_status)
        return query.count()


# Global instance
contact_crud = ContactCRUD()