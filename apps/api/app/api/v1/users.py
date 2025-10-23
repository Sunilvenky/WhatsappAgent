"""
User management routes (admin only).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.schemas.auth import User, UserCreate, UserUpdate
from apps.api.app.crud.user import get_user, create_user, update_user
from apps.api.app.auth.dependencies import require_admin
from apps.api.app.models.user import User as UserModel

router = APIRouter()


@router.get("/", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """List all users (admin only)."""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=User)
async def create_user_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """Create a new user (admin only)."""
    user = create_user(db, user_data)
    return user


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """Get user by ID (admin only)."""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user_admin(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_admin)
):
    """Update user (admin only)."""
    user = update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user