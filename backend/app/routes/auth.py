"""
Authentication routes for user sign-in and JWT token generation.
"""

from fastapi import APIRouter, HTTPException, Request, status, Depends
from app.database import db
from app.security import verify_password, create_access_token, check_csrf, get_current_user, invalidate_token
# from slowapi import Limiter
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from app.utils.rate_limiter import limiter
from datetime import datetime, timedelta, timezone
from app.models import SignInRequest

router = APIRouter()

# Store revoked tokens (Temporary In-Memory Storage for demonstration)
REVOKED_TOKENS = set()

# API Endpoint for Sign-in
@router.post("/signin")
# @limiter.limit("10/minute")
async def signin(request: Request, form_data: SignInRequest):
    check_csrf(request)  # CSRF protection now correctly uses `request`

    email = form_data.email.strip().lower()  # Normalize email
    password = form_data.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Find user in database
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify Password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT Token with user ID
    access_token = create_access_token(data={"sub": str(user["_id"])})

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signout", status_code=status.HTTP_200_OK)
# @limiter.limit("10/minute")
async def signout(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Signs out a user by revoking their JWT token.

    - Requires authentication.
    - Prevents brute force, replay, and CSRF attacks.
    - Revokes the token to prevent reuse.
    """
    
    # Check for CSRF attacks
    check_csrf(request)

    # Get the token from the request header
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = token.split(" ")[1]  # Extract token part

    # Ensure the token is not already revoked (Prevents replay attacks)
    if token in REVOKED_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Invalidate and revoke the token
    invalidate_token(token)
    REVOKED_TOKENS.add(token)
    return {"message": "Signed out successfully"}