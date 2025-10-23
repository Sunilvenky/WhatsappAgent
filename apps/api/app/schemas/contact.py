"""Pydantic schemas for Contact and PhoneNumber models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Contact schemas
class ContactBase(BaseModel):
    """Base schema for Contact."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    opt_in_status: bool = True
    tags: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)


class ContactCreate(ContactBase):
    """Schema for creating a contact."""
    pass


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    opt_in_status: Optional[bool] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100)


class Contact(ContactBase):
    """Schema for Contact response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    opt_in_date: Optional[datetime] = None
    opt_out_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_contacted: Optional[datetime] = None
    
    # Computed properties
    full_name: str
    is_opted_in: bool


# PhoneNumber schemas
class PhoneNumberBase(BaseModel):
    """Base schema for PhoneNumber."""
    number: str = Field(..., min_length=7, max_length=20)
    country_code: str = Field(..., min_length=1, max_length=5)
    type: str = Field(default="mobile", max_length=20)
    is_primary: bool = False
    is_active: bool = True


class PhoneNumberCreate(PhoneNumberBase):
    """Schema for creating a phone number."""
    contact_id: int


class PhoneNumberUpdate(BaseModel):
    """Schema for updating a phone number."""
    number: Optional[str] = Field(None, min_length=7, max_length=20)
    country_code: Optional[str] = Field(None, min_length=1, max_length=5)
    type: Optional[str] = Field(None, max_length=20)
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class PhoneNumber(PhoneNumberBase):
    """Schema for PhoneNumber response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    contact_id: int
    is_whatsapp_verified: bool
    whatsapp_id: Optional[str] = None
    verification_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    formatted_number: str
    is_mobile: bool


# Extended Contact schema with phone numbers
class ContactWithPhones(Contact):
    """Contact schema with phone numbers included."""
    phone_numbers: List[PhoneNumber] = []


# Phone number verification schemas
class PhoneNumberVerify(BaseModel):
    """Schema for verifying a phone number for WhatsApp."""
    whatsapp_id: Optional[str] = None


# Search and filter schemas
class ContactSearch(BaseModel):
    """Schema for contact search parameters."""
    search: Optional[str] = None
    company: Optional[str] = None
    opt_in_status: Optional[bool] = None
    skip: int = 0
    limit: int = 100


class ContactStats(BaseModel):
    """Schema for contact statistics."""
    total_contacts: int
    opted_in: int
    opted_out: int
    with_whatsapp: int
    without_email: int


# Aliases for backwards compatibility
ContactResponse = Contact
PhoneNumberResponse = PhoneNumber
ContactSearchParams = ContactSearch