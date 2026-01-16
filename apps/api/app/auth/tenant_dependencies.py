"""
Tenant dependencies and middleware for multi-tenancy support.
"""
from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from apps.api.app.core.database import get_db
from apps.api.app.models import Tenant, TenantUser, APIKey, User
from apps.api.app.auth.dependencies import get_current_active_user
import hashlib


async def get_current_tenant_id_from_header(
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> int:
    """
    Extract tenant ID from headers and validate user has access.
    
    Priority:
    1. X-Tenant-ID header (if provided)
    2. User's primary tenant (if user belongs to single tenant)
    3. None (error)
    """
    if x_tenant_id:
        try:
            tenant_id = int(x_tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tenant ID format"
            )
    else:
        # Get user's primary tenant
        user_tenant = db.query(TenantUser).filter(
            TenantUser.user_id == current_user.id,
            TenantUser.is_active == True
        ).first()
        
        if not user_tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not associated with any active tenant"
            )
        tenant_id = user_tenant.tenant_id
    
    # Verify user has access to this tenant
    has_access = db.query(TenantUser).filter(
        TenantUser.tenant_id == tenant_id,
        TenantUser.user_id == current_user.id,
        TenantUser.is_active == True
    ).first()
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    return tenant_id


async def get_current_tenant(
    tenant_id: int = Depends(get_current_tenant_id_from_header),
    db: Session = Depends(get_db)
) -> Tenant:
    """Get the current tenant and verify it's active."""
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id,
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive"
        )
    
    return tenant


async def get_tenant_from_api_key(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Authenticate using API key and return associated tenant.
    Used for external API integrations.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # Hash the API key for comparison
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    
    api_key = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    
    # Check if API key has expired
    from datetime import datetime
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    # Update last used timestamp
    api_key.last_used = datetime.utcnow()
    db.commit()
    
    # Get and verify tenant
    tenant = db.query(Tenant).filter(
        Tenant.id == api_key.tenant_id,
        Tenant.is_active == True
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


def get_tenant_from_domain(domain: str, db: Session) -> Optional[Tenant]:
    """
    Resolve tenant from custom domain.
    Useful for multi-tenant SaaS with custom domains.
    """
    tenant = db.query(Tenant).filter(
        Tenant.domain == domain,
        Tenant.is_active == True
    ).first()
    return tenant


def get_tenant_from_slug(slug: str, db: Session) -> Optional[Tenant]:
    """
    Resolve tenant from slug (subdomain-like).
    Example: api.company.com/api/v1/... where "company" is the slug.
    """
    tenant = db.query(Tenant).filter(
        Tenant.slug == slug,
        Tenant.is_active == True
    ).first()
    return tenant
