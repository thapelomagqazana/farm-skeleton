"""
Pydantic models for User data validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base schema for user data."""
    name: str
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user registration, requiring a password."""
    password: str

class UserUpdate(BaseModel):
    """Schema for updating user details."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    """Schema for returning user details, including timestamps."""
    created: datetime
    updated: datetime
