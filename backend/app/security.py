"""
Handles password hashing and JWT authentication.
"""

from passlib.context import CryptContext
from fastapi import HTTPException, Request
from datetime import datetime, timedelta, timezone
from jose import jwt
import os

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables for JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a given password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Generates a JWT access token.

    :param data: Payload to encode in JWT.
    :param expires_delta: Expiry time for the token.
    :return: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# CSRF Protection: Reject requests from unknown origins
def check_csrf(request: Request):
    allowed_origins = {"http://localhost:3000", "https://my-trusted-site.com"}
    referer = request.headers.get("Referer")

    if referer and not any(referer.startswith(origin) for origin in allowed_origins):
        raise HTTPException(status_code=403, detail="CSRF attack detected")
