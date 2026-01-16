"""
CRUD operations for tenant models.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from apps.api.app.models import Tenant, TenantUser, APIKey, UsageRecord, User
from apps.api.app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantUserCreate, TenantUserUpdate,
    APIKeyCreate, APIKeyCreateResponse
)
import hashlib
import secrets
import string


class TenantCRUD:
    """CRUD operations for Tenant model."""
    
    @staticmethod
    def create(db: Session, tenant: TenantCreate) -> Tenant:
        """Create a new tenant."""
        db_tenant = Tenant(
            name=tenant.name,
            slug=tenant.slug,
            domain=tenant.domain,
            plan=tenant.plan,
            settings=tenant.settings or {},
            is_active=True
        )
        db.add(db_tenant)
        db.commit()
        db.refresh(db_tenant)
        return db_tenant
    
    @staticmethod
    def get_by_id(db: Session, tenant_id: int) -> Optional[Tenant]:
        """Get tenant by ID."""
        return db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        return db.query(Tenant).filter(Tenant.slug == slug).first()
    
    @staticmethod
    def get_by_domain(db: Session, domain: str) -> Optional[Tenant]:
        """Get tenant by domain."""
        return db.query(Tenant).filter(Tenant.domain == domain).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants."""
        return db.query(Tenant).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, tenant_id: int, tenant_update: TenantUpdate) -> Optional[Tenant]:
        """Update a tenant."""
        db_tenant = TenantCRUD.get_by_id(db, tenant_id)
        if not db_tenant:
            return None
        
        update_data = tenant_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tenant, field, value)
        
        db.commit()
        db.refresh(db_tenant)
        return db_tenant
    
    @staticmethod
    def delete(db: Session, tenant_id: int) -> bool:
        """Delete a tenant (soft delete by setting is_active=False)."""
        db_tenant = TenantCRUD.get_by_id(db, tenant_id)
        if not db_tenant:
            return False
        
        db_tenant.is_active = False
        db.commit()
        return True


class TenantUserCRUD:
    """CRUD operations for TenantUser model."""
    
    @staticmethod
    def create(db: Session, tenant_id: int, tenant_user: TenantUserCreate, invited_by: Optional[int] = None) -> TenantUser:
        """Add a user to a tenant."""
        db_tenant_user = TenantUser(
            tenant_id=tenant_id,
            user_id=tenant_user.user_id,
            role=tenant_user.role,
            invited_by=invited_by,
            is_active=True
        )
        db.add(db_tenant_user)
        db.commit()
        db.refresh(db_tenant_user)
        return db_tenant_user
    
    @staticmethod
    def get_by_id(db: Session, tenant_user_id: int) -> Optional[TenantUser]:
        """Get tenant user by ID."""
        return db.query(TenantUser).filter(TenantUser.id == tenant_user_id).first()
    
    @staticmethod
    def get_by_tenant_and_user(db: Session, tenant_id: int, user_id: int) -> Optional[TenantUser]:
        """Get tenant user by tenant and user ID."""
        return db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
    
    @staticmethod
    def get_user_tenants(db: Session, user_id: int) -> List[TenantUser]:
        """Get all tenants for a user."""
        return db.query(TenantUser).filter(
            TenantUser.user_id == user_id,
            TenantUser.is_active == True
        ).all()
    
    @staticmethod
    def get_tenant_users(db: Session, tenant_id: int) -> List[TenantUser]:
        """Get all users in a tenant."""
        return db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.is_active == True
        ).all()
    
    @staticmethod
    def update(db: Session, tenant_user_id: int, tenant_user_update: TenantUserUpdate) -> Optional[TenantUser]:
        """Update tenant user role or status."""
        db_tenant_user = TenantUserCRUD.get_by_id(db, tenant_user_id)
        if not db_tenant_user:
            return None
        
        update_data = tenant_user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_tenant_user, field, value)
        
        db.commit()
        db.refresh(db_tenant_user)
        return db_tenant_user
    
    @staticmethod
    def remove_from_tenant(db: Session, tenant_id: int, user_id: int) -> bool:
        """Remove user from tenant (soft delete)."""
        db_tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, user_id)
        if not db_tenant_user:
            return False
        
        db_tenant_user.is_active = False
        db.commit()
        return True


class APIKeyCRUD:
    """CRUD operations for APIKey model."""
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a new API key."""
        chars = string.ascii_letters + string.digits + "-_"
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def hash_api_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def create(db: Session, tenant_id: int, api_key_create: APIKeyCreate) -> tuple[APIKey, str]:
        """Create a new API key for a tenant."""
        # Generate and hash key
        raw_key = APIKeyCRUD.generate_api_key()
        key_hash = APIKeyCRUD.hash_api_key(raw_key)
        
        db_api_key = APIKey(
            tenant_id=tenant_id,
            name=api_key_create.name,
            key_hash=key_hash,
            permissions=api_key_create.permissions,
            rate_limit=api_key_create.rate_limit,
            description=api_key_create.description,
            expires_at=api_key_create.expires_at,
            is_active=True
        )
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        return db_api_key, raw_key
    
    @staticmethod
    def get_by_id(db: Session, api_key_id: int) -> Optional[APIKey]:
        """Get API key by ID."""
        return db.query(APIKey).filter(APIKey.id == api_key_id).first()
    
    @staticmethod
    def get_by_tenant(db: Session, tenant_id: int) -> List[APIKey]:
        """Get all API keys for a tenant."""
        return db.query(APIKey).filter(
            APIKey.tenant_id == tenant_id,
            APIKey.is_active == True
        ).all()
    
    @staticmethod
    def verify_and_get(db: Session, raw_key: str) -> Optional[APIKey]:
        """Verify a raw API key and return the API key object."""
        key_hash = APIKeyCRUD.hash_api_key(raw_key)
        return db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        ).first()
    
    @staticmethod
    def revoke(db: Session, api_key_id: int) -> bool:
        """Revoke an API key."""
        db_api_key = APIKeyCRUD.get_by_id(db, api_key_id)
        if not db_api_key:
            return False
        
        db_api_key.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def update(db: Session, api_key_id: int, **kwargs) -> Optional[APIKey]:
        """Update API key fields."""
        db_api_key = APIKeyCRUD.get_by_id(db, api_key_id)
        if not db_api_key:
            return None
        
        for field, value in kwargs.items():
            if hasattr(db_api_key, field):
                setattr(db_api_key, field, value)
        
        db.commit()
        db.refresh(db_api_key)
        return db_api_key


class UsageRecordCRUD:
    """CRUD operations for UsageRecord model."""
    
    @staticmethod
    def get_or_create_today(db: Session, tenant_id: int) -> UsageRecord:
        """Get or create usage record for today."""
        today = datetime.utcnow().date()
        
        record = db.query(UsageRecord).filter(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.date >= datetime.combine(today, datetime.min.time()),
            UsageRecord.date < datetime.combine(today, datetime.max.time())
        ).first()
        
        if not record:
            record = UsageRecord(
                tenant_id=tenant_id,
                date=datetime.utcnow()
            )
            db.add(record)
            db.commit()
            db.refresh(record)
        
        return record
    
    @staticmethod
    def increment_messages_sent(db: Session, tenant_id: int, count: int = 1) -> None:
        """Increment messages sent count."""
        record = UsageRecordCRUD.get_or_create_today(db, tenant_id)
        record.messages_sent += count
        db.commit()
    
    @staticmethod
    def increment_api_calls(db: Session, tenant_id: int, count: int = 1) -> None:
        """Increment API calls count."""
        record = UsageRecordCRUD.get_or_create_today(db, tenant_id)
        record.api_calls += count
        db.commit()
    
    @staticmethod
    def get_monthly_usage(db: Session, tenant_id: int) -> dict:
        """Get monthly usage statistics."""
        from datetime import timedelta
        today = datetime.utcnow()
        month_ago = today - timedelta(days=30)
        
        records = db.query(UsageRecord).filter(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.date >= month_ago
        ).all()
        
        total_messages = sum(r.messages_sent for r in records)
        total_api_calls = sum(r.api_calls for r in records)
        
        return {
            "messages_sent": total_messages,
            "api_calls": total_api_calls,
            "period_days": 30
        }
    
    @staticmethod
    def get_daily_usage(db: Session, tenant_id: int, days: int = 30) -> List[UsageRecord]:
        """Get usage records for the last N days."""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        return db.query(UsageRecord).filter(
            UsageRecord.tenant_id == tenant_id,
            UsageRecord.date >= date_from
        ).order_by(UsageRecord.date.desc()).all()
