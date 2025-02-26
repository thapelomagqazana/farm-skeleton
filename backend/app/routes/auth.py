"""
Authentication routes for user sign-in and JWT token generation.
"""

from fastapi import APIRouter, HTTPException, Request
from app.database import db
from app.security import verify_password, create_access_token, check_csrf
from datetime import datetime, timedelta, timezone
from app.models import SignInRequest

router = APIRouter()


# Rate limiting (Prevent brute-force attacks)
FAILED_ATTEMPTS = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TIME = 60  # Lock for 60 seconds after MAX_FAILED_ATTEMPTS

# API Endpoint for Sign-in
@router.post("/signin")
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

    # Brute Force Protection
    if email in FAILED_ATTEMPTS and FAILED_ATTEMPTS[email]["count"] >= MAX_FAILED_ATTEMPTS:
        last_attempt = FAILED_ATTEMPTS[email]["last_attempt"]
        if (datetime.now(timezone.utc) - last_attempt).total_seconds() < LOCKOUT_TIME:
            raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
        else:
            FAILED_ATTEMPTS[email] = {"count": 0, "last_attempt": datetime.now(timezone.utc)}

    # Verify Password
    if not verify_password(password, user["password"]):
        if email not in FAILED_ATTEMPTS:
            FAILED_ATTEMPTS[email] = {"count": 1, "last_attempt": datetime.now(timezone.utc)}
        else:
            FAILED_ATTEMPTS[email]["count"] += 1
            FAILED_ATTEMPTS[email]["last_attempt"] = datetime.now(timezone.utc)

        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Reset failed attempts on success
    if email in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS[email] = {"count": 0, "last_attempt": datetime.now(timezone.utc)}

    # Generate JWT Token with user ID
    access_token = create_access_token(data={"sub": str(user["_id"])})

    return {"access_token": access_token, "token_type": "bearer"}