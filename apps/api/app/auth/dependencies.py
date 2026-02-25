"""
Authentication dependencies for FastAPI.
"""
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from apps.api.app.core.database import get_db
from apps.api.app.models.user import User, UserRole
from apps.api.app.auth.utils import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    identifier = verify_token(token)
    if identifier is None:
        raise credentials_exception
    
    # Try looking up by username or email
    user = db.query(User).filter((User.username == identifier) | (User.email == identifier)).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_roles(allowed_roles: List[UserRole]):
    """Create a dependency that requires specific roles."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


# Role-specific dependencies
require_admin = require_roles([UserRole.ADMIN])
require_marketer = require_roles([UserRole.ADMIN, UserRole.MARKETER])
require_sales = require_roles([UserRole.ADMIN, UserRole.MARKETER, UserRole.SALES])