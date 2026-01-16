"""
Tenant management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from apps.api.app.core.database import get_db
from apps.api.app.auth.dependencies import get_current_active_user
from apps.api.app.auth.tenant_dependencies import get_current_tenant, get_current_tenant_id_from_header
from apps.api.app.models import User, Tenant
from apps.api.app.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantResponse,
    TenantUserCreate, TenantUserUpdate, TenantUserResponse,
    APIKeyCreate, APIKeyResponse, APIKeyCreateResponse,
    UsageStatsResponse
)
from apps.api.app.crud.tenant import TenantCRUD, TenantUserCRUD, APIKeyCRUD, UsageRecordCRUD

router = APIRouter(prefix="/api/v1/tenants", tags=["Tenants"])


# ==================== TENANT ENDPOINTS ====================

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new tenant.
    Only super-admins can create tenants.
    """
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create tenants"
        )
    
    # Check if slug already exists
    existing = TenantCRUD.get_by_slug(db, tenant.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug already exists"
        )
    
    # Create tenant
    db_tenant = TenantCRUD.create(db, tenant)
    
    # Add creator as owner
    owner_tenant_user = TenantUserCreate(role="owner")
    TenantUserCRUD.create(db, db_tenant.id, owner_tenant_user, invited_by=current_user.id)
    
    return db_tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get tenant details."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_update: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Update tenant settings."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only owners/admins can update
    tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, current_user.id)
    if not tenant_user or tenant_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners/admins can update tenant"
        )
    
    updated = TenantCRUD.update(db, tenant_id, tenant_update)
    return updated


# ==================== TENANT USERS ENDPOINTS ====================

@router.get("/{tenant_id}/users", response_model=List[TenantUserResponse])
async def get_tenant_users(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get all users in a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    users = TenantUserCRUD.get_tenant_users(db, tenant_id)
    return users


@router.post("/{tenant_id}/users", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_tenant(
    tenant_id: int,
    tenant_user: TenantUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Add a user to a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only owners/admins can add users
    current_tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, current_user.id)
    if not current_tenant_user or current_tenant_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners/admins can add users"
        )
    
    # Check if user exists
    user_to_add = db.query(User).filter(User.id == tenant_user.user_id).first()
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already member
    existing = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, tenant_user.user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this tenant"
        )
    
    # Add user
    new_tenant_user = TenantUserCRUD.create(db, tenant_id, tenant_user, invited_by=current_user.id)
    return new_tenant_user


@router.put("/{tenant_id}/users/{user_id}", response_model=TenantUserResponse)
async def update_tenant_user(
    tenant_id: int,
    user_id: int,
    tenant_user_update: TenantUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Update a user's role in a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only owners can modify user roles
    current_tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, current_user.id)
    if not current_tenant_user or current_tenant_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can modify user roles"
        )
    
    tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, user_id)
    if not tenant_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in tenant"
        )
    
    updated = TenantUserCRUD.update(db, tenant_user.id, tenant_user_update)
    return updated


@router.delete("/{tenant_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_tenant(
    tenant_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Remove a user from a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only owners can remove users
    current_tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, current_user.id)
    if not current_tenant_user or current_tenant_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can remove users"
        )
    
    success = TenantUserCRUD.remove_from_tenant(db, tenant_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in tenant"
        )


# ==================== API KEYS ENDPOINTS ====================

@router.post("/{tenant_id}/api-keys", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    tenant_id: int,
    api_key: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Create a new API key for a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only admins can create API keys
    tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, current_user.id)
    if not tenant_user or tenant_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create API keys"
        )
    
    db_api_key, raw_key = APIKeyCRUD.create(db, tenant_id, api_key)
    
    return {
        "id": db_api_key.id,
        "tenant_id": db_api_key.tenant_id,
        "name": db_api_key.name,
        "permissions": db_api_key.permissions,
        "rate_limit": db_api_key.rate_limit,
        "description": db_api_key.description,
        "is_active": db_api_key.is_active,
        "last_used": db_api_key.last_used,
        "created_at": db_api_key.created_at,
        "key": raw_key  # Only returned once
    }


@router.get("/{tenant_id}/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get all API keys for a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    keys = APIKeyCRUD.get_by_tenant(db, tenant_id)
    return keys


@router.delete("/{tenant_id}/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    tenant_id: int,
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Revoke an API key."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only admins can revoke keys
    tenant_user = TenantUserCRUD.get_by_tenant_and_user(db, tenant_id, current_user.id)
    if not tenant_user or tenant_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can revoke keys"
        )
    
    success = APIKeyCRUD.revoke(db, key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )


# ==================== USAGE & BILLING ENDPOINTS ====================

@router.get("/{tenant_id}/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """Get usage statistics for a tenant."""
    if current_tenant.id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    usage = UsageRecordCRUD.get_monthly_usage(db, tenant_id)
    
    # Get plan limits (mock - implement based on your plan tiers)
    plan_limits = {
        "free": {"messages": 100, "contacts": 50},
        "starter": {"messages": 2000, "contacts": 500},
        "pro": {"messages": 10000, "contacts": 5000},
        "enterprise": {"messages": None, "contacts": None}
    }
    
    limits = plan_limits.get(current_tenant.plan, {})
    
    return {
        "tenant_id": tenant_id,
        "messages_sent_today": 0,  # Would query from today's record
        "messages_sent_this_month": usage["messages_sent"],
        "api_calls_today": 0,
        "api_calls_this_month": usage["api_calls"],
        "total_contacts": 0,
        "total_conversations": 0,
        "plan": current_tenant.plan,
        "plan_message_limit": limits.get("messages"),
        "plan_contact_limit": limits.get("contacts")
    }
