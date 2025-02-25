"""
Authentication routes for user sign-in and JWT token generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.security import verify_password, create_access_token
from datetime import timedelta
from app.models import UserCreate
from pydantic import BaseModel

router = APIRouter()

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: str
    password: str

@router.post("/signin", response_model=Token)
async def signin(credentials: LoginRequest):
    """
    Authenticate user and return JWT token.

    :param credentials: LoginRequest schema.
    :return: JWT access token.
    """
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user["_id"])}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
