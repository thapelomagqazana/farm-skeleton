"""
Handles password hashing and JWT authentication.
"""

from passlib.context import CryptContext
from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.database import db
from bson import ObjectId
import os

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Load environment variables for JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin")

# Store revoked tokens temporarily (or use a DB)
REVOKED_TOKENS = set()


def invalidate_token(token: str):
    """Adds the token to the revoked list."""
    REVOKED_TOKENS.add(token)

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
    
# Function to Decode JWT Token and Fetch User by ID
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verifies JWT token and retrieves the authenticated user by ID."""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # Extract user ID from token

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Validate ObjectId format
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Fetch user from database using user_id
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 1, "name": 1, "email": 1, "role": 1})

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Ensure role exists
        if "role" not in user:
            user["role"] = "user"  # Default role

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

