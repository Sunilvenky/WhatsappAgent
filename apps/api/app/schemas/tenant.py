"""
Pydantic schemas for tenant models.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


# Tenant Schemas
class TenantBase(BaseModel):
    name: str
    slug: str
    domain: Optional[str] = None
    plan: str = "free"
    settings: Optional[Dict[str, Any]] = {}


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    plan: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    id: int
    billing_customer_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tenant User Schemas
class TenantUserBase(BaseModel):
    role: str = "member"


class TenantUserCreate(TenantUserBase):
    user_id: int


class TenantUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class TenantUserResponse(TenantUserBase):
    id: int
    tenant_id: int
    user_id: int
    is_active: bool
    joined_at: datetime

    class Config:
        from_attributes = True


class TenantUserInviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"
    invited_by: int


class TenantUserInviteResponse(BaseModel):
    id: int
    tenant_id: int
    email: str
    role: str
    invited_at: datetime
    accepted: bool


# API Key Schemas
class APIKeyBase(BaseModel):
    name: str
    permissions: List[str] = ["read", "write"]
    rate_limit: int = 1000
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyResponse(APIKeyBase):
    id: int
    tenant_id: int
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreateResponse(APIKeyResponse):
    key: str  # Only returned on creation


# Usage Record Schemas
class UsageRecordResponse(BaseModel):
    id: int
    tenant_id: int
    date: datetime
    messages_sent: int
    messages_delivered: int
    messages_failed: int
    api_calls: int
    contacts_count: int
    conversations_count: int

    class Config:
        from_attributes = True


class UsageStatsResponse(BaseModel):
    tenant_id: int
    messages_sent_today: int
    messages_sent_this_month: int
    api_calls_today: int
    api_calls_this_month: int
    total_contacts: int
    total_conversations: int
    plan: str
    plan_message_limit: Optional[int]
    plan_contact_limit: Optional[int]
