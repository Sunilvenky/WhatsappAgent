"""
Authentication and user schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from apps.api.app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.SALES
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class User(UserInDB):
    pass


class LoginRequest(BaseModel):
    username: str
    password: str