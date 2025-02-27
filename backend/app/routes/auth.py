"""
Authentication routes for user sign-in and JWT token generation.
"""
import logging
from fastapi import APIRouter, HTTPException, Request, Depends
from app.database import db
from app.security import verify_password, create_access_token, check_csrf, get_current_user, invalidate_token
from app.models import SignInRequest, TokenResponse, LogoutResponse

router = APIRouter()

# Store revoked tokens (Temporary In-Memory Storage for demonstration)
REVOKED_TOKENS = set()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)


@router.post("/signin", response_model=TokenResponse, tags=["Authentication"], summary="User Sign-In")
async def signin(request: Request, form_data: SignInRequest):
    """
    Authenticates a user and returns a JWT token.

    - **Requires:** Email & Password
    - **Returns:** A JWT token for future authenticated requests
    """
    check_csrf(request)

    email = form_data.email.strip().lower()
    password = form_data.password

    if not email or not password:
        logger.warning(f"Signin attempt failed: Missing credentials - IP: {request.client.host}")
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        logger.warning(f"Failed login attempt for email: {email} - IP: {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user["_id"])})

    logger.info(f"User signed in: {email} - IP: {request.client.host}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signout", response_model=LogoutResponse, tags=["Authentication"], summary="User Sign-Out")
async def signout(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Logs out a user by revoking their JWT token.

    - **Requires:** Authentication token in header
    - **Ensures:** Token cannot be reused (prevents replay attacks)
    """
    check_csrf(request)

    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        logger.warning(f"Signout attempt failed: No token provided - User: {current_user['email']}")
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = token.split(" ")[1]
    if token in REVOKED_TOKENS:
        logger.warning(f"Replay attack detected for token: {token} - User: {current_user['email']}")
        raise HTTPException(status_code=401, detail="Invalid token")

    invalidate_token(token)
    REVOKED_TOKENS.add(token)

    logger.info(f"User signed out: {current_user['email']}")
    return {"message": "Signed out successfully"}