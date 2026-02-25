"""Contact management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.crud import contact_crud, phone_number_crud
from apps.api.app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactSearchParams,
    PhoneNumberCreate,
    PhoneNumberUpdate,
    PhoneNumberResponse
)
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contact."""
    try:
        db_contact = contact_crud.create(db, **contact.model_dump())
        return db_contact
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create contact: {str(e)}"
        )


@router.get("/", response_model=List[ContactResponse])
def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    opt_in_status: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List contacts with optional filtering."""
    search_params = ContactSearchParams(
        search=search,
        company=company,
        opt_in_status=opt_in_status,
        skip=skip,
        limit=limit
    )
    
    contacts = contact_crud.get_multi(
        db, 
        **search_params.model_dump()
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contact by ID."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a contact."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    updated_contact = contact_crud.update(db, contact, **contact_update.model_dump(exclude_unset=True))
    return updated_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a contact."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    contact_crud.delete(db, contact_id)


@router.post("/{contact_id}/opt-in", response_model=ContactResponse)
def opt_in_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Opt in a contact to marketing communications."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    updated_contact = contact_crud.opt_in(db, contact_id)
    return updated_contact


@router.post("/{contact_id}/opt-out", response_model=ContactResponse)
def opt_out_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Opt out a contact from marketing communications."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    updated_contact = contact_crud.opt_out(db, contact_id)
    return updated_contact


@router.get("/{contact_id}/phone-numbers", response_model=List[PhoneNumberResponse])
def get_contact_phone_numbers(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all phone numbers for a contact."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    phone_numbers = phone_number_crud.get_by_contact(db, contact_id)
    return phone_numbers


@router.post("/{contact_id}/phone-numbers", response_model=PhoneNumberResponse, status_code=status.HTTP_201_CREATED)
def add_phone_number(
    contact_id: int,
    phone_data: PhoneNumberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a phone number to a contact."""
    contact = contact_crud.get(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    # Check if phone number already exists
    existing_phone = phone_number_crud.get_by_number(db, phone_data.number)
    if existing_phone and existing_phone.contact_id != contact_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is already associated with another contact"
        )
    
    phone_number = phone_number_crud.create(
        db,
        contact_id=contact_id,
        **phone_data.model_dump()
    )
    return phone_number


@router.put("/phone-numbers/{phone_id}", response_model=PhoneNumberResponse)
def update_phone_number(
    phone_id: int,
    phone_update: PhoneNumberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a phone number."""
    phone = phone_number_crud.get(db, phone_id)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    updated_phone = phone_number_crud.update(
        db, 
        phone, 
        **phone_update.model_dump(exclude_unset=True)
    )
    return updated_phone


@router.delete("/phone-numbers/{phone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_phone_number(
    phone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a phone number."""
    phone = phone_number_crud.get(db, phone_id)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    phone_number_crud.delete(db, phone_id)


@router.post("/phone-numbers/{phone_id}/verify", response_model=PhoneNumberResponse)
def verify_whatsapp_number(
    phone_id: int,
    whatsapp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify a phone number for WhatsApp."""
    phone = phone_number_crud.get(db, phone_id)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    verified_phone = phone_number_crud.verify_whatsapp(db, phone_id, whatsapp_id)
    return verified_phone


@router.post("/phone-numbers/{phone_id}/set-primary", response_model=PhoneNumberResponse)
def set_primary_phone(
    phone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set a phone number as primary for a contact."""
    phone = phone_number_crud.get(db, phone_id)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    primary_phone = phone_number_crud.set_primary(db, phone_id)
    return primary_phone


@router.get("/bulk/opt-in-stats")
def get_opt_in_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contact opt-in statistics."""
    stats = contact_crud.get_opt_in_stats(db)
    return stats


@router.post("/bulk/import")
def bulk_import_contacts(
    contacts: List[ContactCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk import contacts."""
    try:
        created_contacts = []
        for contact_data in contacts:
            # Check if contact already exists by email
            existing_contact = contact_crud.get_by_email(db, contact_data.email)
            if existing_contact:
                continue  # Skip existing contacts
            
            contact = contact_crud.create(db, **contact_data.model_dump())
            created_contacts.append(contact)
        
        return {
            "imported": len(created_contacts),
            "skipped": len(contacts) - len(created_contacts),
            "total": len(contacts)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bulk import failed: {str(e)}"
        )