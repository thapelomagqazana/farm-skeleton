"""
Pydantic models for User data validation.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# Base user schema (shared fields)
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's unique email address")


# Schema for user creation
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="User's password")
    role: str = Field(default="user", description="User role (e.g., user, admin)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure name is not empty and doesn't contain scripts"""
        if value.strip() == "":
            raise ValueError("Name must contain characters")
        if "<script>" in value.lower():
            raise ValueError("Invalid characters in name")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Ensure password contains letters, numbers, and special characters"""
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value) or not re.search(r'[\W_]', value):
            raise ValueError("Password must include letters, numbers, and special characters")
        return value


# Schema for updating user details
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None  # Allow updating role

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure name is not empty and doesn't contain scripts"""
        if value.strip() == "":
            raise ValueError("Name must contain characters")
        if "<script>" in value.lower():
            raise ValueError("Invalid characters in name")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Ensure password contains letters, numbers, and special characters"""
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value) or not re.search(r'[\W_]', value):
            raise ValueError("Password must include letters, numbers, and special characters")
        return value


# Schema for returning user details
class UserInDB(UserBase):
    created: datetime
    updated: datetime
    role: str


# Pydantic Model for Sign-in
class SignInRequest(BaseModel):
    email: EmailStr = Field(..., description="User's unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="User's password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Ensure password contains letters, numbers, and special characters"""
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value) or not re.search(r'[\W_]', value):
            raise ValueError("Password must include letters, numbers, and special characters")
        return value


# Pydantic Model for User Response
class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LogoutResponse(BaseModel):
    message: str
