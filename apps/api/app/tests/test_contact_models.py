"""Tests for Contact and PhoneNumber models and CRUD operations."""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from apps.api.app.models.contact import Contact
from apps.api.app.models.phone_number import PhoneNumber
from apps.api.app.crud.contact import contact_crud
from apps.api.app.crud.phone_number import phone_number_crud


class TestContactModel:
    """Test Contact model functionality."""

    def test_create_contact(self, db: Session):
        """Test creating a contact."""
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "company": "Test Corp",
            "opt_in_status": True,
        }
        
        contact = Contact(**contact_data)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        assert contact.id is not None
        assert contact.first_name == "John"
        assert contact.last_name == "Doe"
        assert contact.email == "john.doe@example.com"
        assert contact.is_opted_in is True
        assert contact.full_name == "John Doe"

    def test_contact_opt_out(self, db: Session):
        """Test contact opt-out functionality."""
        contact = Contact(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            opt_in_status=True
        )
        db.add(contact)
        db.commit()
        
        # Opt out
        contact.opt_out()
        db.commit()
        
        assert contact.opt_in_status is False
        assert contact.opt_out_date is not None
        assert contact.is_opted_in is False

    def test_contact_opt_in(self, db: Session):
        """Test contact opt-in functionality."""
        contact = Contact(
            first_name="Bob",
            email="bob@example.com",
            opt_in_status=False
        )
        db.add(contact)
        db.commit()
        
        # Opt in
        contact.opt_in()
        db.commit()
        
        assert contact.opt_in_status is True
        assert contact.opt_in_date is not None
        assert contact.opt_out_date is None


class TestContactCRUD:
    """Test Contact CRUD operations."""

    def test_create_contact_crud(self, db: Session):
        """Test creating a contact via CRUD."""
        contact_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice@example.com",
            "company": "Tech Inc",
        }
        
        contact = contact_crud.create(db, **contact_data)
        
        assert contact.id is not None
        assert contact.first_name == "Alice"
        assert contact.email == "alice@example.com"

    def test_get_contact_by_id(self, db: Session):
        """Test getting a contact by ID."""
        contact = Contact(
            first_name="Charlie",
            email="charlie@example.com"
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        retrieved = contact_crud.get(db, contact.id)
        
        assert retrieved is not None
        assert retrieved.id == contact.id
        assert retrieved.first_name == "Charlie"

    def test_get_contact_by_email(self, db: Session):
        """Test getting a contact by email."""
        contact = Contact(
            first_name="David",
            email="david@example.com"
        )
        db.add(contact)
        db.commit()
        
        retrieved = contact_crud.get_by_email(db, "david@example.com")
        
        assert retrieved is not None
        assert retrieved.email == "david@example.com"
        assert retrieved.first_name == "David"

    def test_search_contacts(self, db: Session):
        """Test searching contacts."""
        contacts = [
            Contact(first_name="Emma", last_name="Wilson", company="Design Co"),
            Contact(first_name="Frank", last_name="Brown", company="Tech Solutions"),
            Contact(first_name="Grace", last_name="Davis", email="grace@tech.com"),
        ]
        
        for contact in contacts:
            db.add(contact)
        db.commit()
        
        # Search by company
        results = contact_crud.search_contacts(db, "Tech")
        assert len(results) == 2
        
        # Search by name
        results = contact_crud.search_contacts(db, "Emma")
        assert len(results) == 1
        assert results[0].first_name == "Emma"

    def test_get_opted_in_contacts(self, db: Session):
        """Test getting opted-in contacts."""
        contacts = [
            Contact(first_name="User1", email="user1@example.com", opt_in_status=True),
            Contact(first_name="User2", email="user2@example.com", opt_in_status=False),
            Contact(first_name="User3", email="user3@example.com", opt_in_status=True),
        ]
        
        for contact in contacts:
            db.add(contact)
        db.commit()
        
        opted_in = contact_crud.get_opted_in_contacts(db)
        
        assert len(opted_in) == 2
        for contact in opted_in:
            assert contact.opt_in_status is True


class TestPhoneNumberModel:
    """Test PhoneNumber model functionality."""

    def test_create_phone_number(self, db: Session):
        """Test creating a phone number."""
        # First create a contact
        contact = Contact(first_name="Test", email="test@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone_data = {
            "contact_id": contact.id,
            "number": "+1234567890",
            "country_code": "+1",
            "type": "mobile",
            "is_primary": True,
        }
        
        phone = PhoneNumber(**phone_data)
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        assert phone.id is not None
        assert phone.number == "+1234567890"
        assert phone.is_mobile is True
        assert phone.formatted_number == "+1234567890"

    def test_phone_number_verification(self, db: Session):
        """Test phone number WhatsApp verification."""
        contact = Contact(first_name="Test", email="test@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone = PhoneNumber(
            contact_id=contact.id,
            number="+1987654321",
            country_code="+1",
        )
        db.add(phone)
        db.commit()
        
        # Verify WhatsApp
        phone.verify_whatsapp("1987654321@c.us")
        db.commit()
        
        assert phone.is_whatsapp_verified is True
        assert phone.whatsapp_id == "1987654321@c.us"


class TestPhoneNumberCRUD:
    """Test PhoneNumber CRUD operations."""

    def test_create_phone_number_crud(self, db: Session):
        """Test creating a phone number via CRUD."""
        contact = Contact(first_name="Test", email="test@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone_data = {
            "contact_id": contact.id,
            "number": "+44123456789",
            "country_code": "+44",
            "type": "mobile",
        }
        
        phone = phone_number_crud.create(db, **phone_data)
        
        assert phone.id is not None
        assert phone.number == "+44123456789"
        assert phone.contact_id == contact.id

    def test_get_phone_by_contact(self, db: Session):
        """Test getting phone numbers for a contact."""
        contact = Contact(first_name="Multi", email="multi@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phones = [
            PhoneNumber(contact_id=contact.id, number="+1111111111", country_code="+1", type="mobile"),
            PhoneNumber(contact_id=contact.id, number="+1222222222", country_code="+1", type="work"),
        ]
        
        for phone in phones:
            db.add(phone)
        db.commit()
        
        retrieved = phone_number_crud.get_by_contact(db, contact.id)
        
        assert len(retrieved) == 2

    def test_set_primary_phone(self, db: Session):
        """Test setting a phone number as primary."""
        contact = Contact(first_name="Primary", email="primary@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone1 = PhoneNumber(contact_id=contact.id, number="+1111111111", country_code="+1")
        phone2 = PhoneNumber(contact_id=contact.id, number="+1222222222", country_code="+1")
        
        db.add(phone1)
        db.add(phone2)
        db.commit()
        db.refresh(phone1)
        db.refresh(phone2)
        
        # Set phone2 as primary
        result = phone_number_crud.set_as_primary(db, phone2.id)
        
        assert result is True
        
        # Refresh and check
        db.refresh(phone1)
        db.refresh(phone2)
        
        assert phone1.is_primary is False
        assert phone2.is_primary is True

    def test_verify_whatsapp_crud(self, db: Session):
        """Test WhatsApp verification via CRUD."""
        contact = Contact(first_name="WhatsApp", email="whatsapp@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        phone = PhoneNumber(
            contact_id=contact.id,
            number="+1555555555",
            country_code="+1"
        )
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        # Verify WhatsApp
        result = phone_number_crud.verify_whatsapp(db, phone.id, "1555555555@c.us")
        
        assert result is True
        
        db.refresh(phone)
        assert phone.is_whatsapp_verified is True
        assert phone.whatsapp_id == "1555555555@c.us"

    def test_get_verified_whatsapp_numbers(self, db: Session):
        """Test getting verified WhatsApp numbers."""
        contact = Contact(first_name="Verified", email="verified@example.com")
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        verified_phone = PhoneNumber(
            contact_id=contact.id,
            number="+1777777777",
            country_code="+1",
            is_whatsapp_verified=True,
            whatsapp_id="1777777777@c.us"
        )
        
        unverified_phone = PhoneNumber(
            contact_id=contact.id,
            number="+1888888888",
            country_code="+1",
            is_whatsapp_verified=False
        )
        
        db.add(verified_phone)
        db.add(unverified_phone)
        db.commit()
        
        verified_numbers = phone_number_crud.get_verified_whatsapp_numbers(db)
        
        assert len(verified_numbers) >= 1
        for phone in verified_numbers:
            assert phone.is_whatsapp_verified is True