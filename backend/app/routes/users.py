from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from app.database import db
from app.models import UserCreate, UserUpdate, UserInDB, UserResponse
from app.security import hash_password, get_current_user
from bson import ObjectId
from datetime import datetime, timezone
import re

router = APIRouter()

# Constants for error messages
ERROR_404_MESSAGE = "User not found"
ERROR_400_EMAIL_EXISTS_MESSAGE = "Email already registered"
ERROR_403_FORBIDDEN_ACCESS_MESSAGE = "Forbidden: Access denied"

# Rate limiting setup
RATE_LIMIT_TRACKER = {}
MAX_REQUESTS = 10  # Maximum allowed requests
TIME_FRAME = 60  # 60 seconds time window


@router.post("/test/reset_rate_limit")
async def reset_rate_limit(request: Request):
    """Resets the rate limiting tracker for testing."""
    global RATE_LIMIT_TRACKER
    RATE_LIMIT_TRACKER = {}  # Reset
    return {"message": "Rate limiting reset"}

async def rate_limit_check(request: Request):
    """Prevents excessive requests (Brute Force Protection)"""
    client_ip = request.client.host  # Get client's IP address
    now = datetime.now(timezone.utc)

    if client_ip not in RATE_LIMIT_TRACKER:
        RATE_LIMIT_TRACKER[client_ip] = []

    RATE_LIMIT_TRACKER[client_ip].append(now)

    # Remove expired requests outside of the TIME_FRAME
    RATE_LIMIT_TRACKER[client_ip] = [
        t for t in RATE_LIMIT_TRACKER[client_ip] if (now - t).total_seconds() < TIME_FRAME
    ]

    if len(RATE_LIMIT_TRACKER[client_ip]) > MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user with hashed password.

    :param user: UserCreate schema.
    :return: ID of the newly created user.
    """
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail=ERROR_400_EMAIL_EXISTS_MESSAGE)

    hashed_password = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "role": user.role if user.role else "user",  # Ensure role is stored
        "created": datetime.now(timezone.utc),
        "updated": datetime.now(timezone.utc)
    }
    result = await db.users.insert_one(new_user)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="User creation failed")
    
    return {"id": str(result.inserted_id), "message": "User created successfully"}

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    request: Request, 
    current_user: dict = Depends(get_current_user),  # Requires authentication
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    limit: int = Query(10, ge=1, description="Limit per page (default: 10, max: 100)"),
):
    """Retrieves a paginated list of users."""
    await rate_limit_check(request)  # Apply rate limiting

    # Cap `limit` to 100 instead of rejecting it
    if limit > 100:
        limit = 100  # Set a max limit internally
    
    # Prevent SQL Injection or Non-Numeric Queries
    if not isinstance(page, int) or not isinstance(limit, int):
        raise HTTPException(status_code=400, detail="Invalid pagination values")
    
    # Ensure only admins can fetch all users
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail=ERROR_403_FORBIDDEN_ACCESS_MESSAGE)

    # Count total users
    total_users = await db.users.count_documents({})
    if total_users == 0:
        return []

    # Fetch users with pagination
    skip = (page - 1) * limit
    users_cursor = db.users.find({}, {"_id": 1, "name": 1, "email": 1, "created_at": 1}).skip(skip).limit(limit)
    users_list = await users_cursor.to_list(length=limit)

    return [
            UserResponse(
                id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                created_at=user.get("created_at", datetime.now(timezone.utc).isoformat()),
            ) for user in users_list
        ]

# Helper function to validate ObjectId format
def is_valid_objectid(user_id: str) -> bool:
    return ObjectId.is_valid(user_id)

# GET /api/users/{user_id} - Fetch a specific user by ID
@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(request: Request, user_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch a user by ID with proper authentication and security checks.

    - Requires authentication.
    - Checks for valid ObjectId format.
    - Ensures proper authorization.
    """
    await rate_limit_check(request)  # Apply rate limiting

    user_id = user_id.strip()  # Trim spaces

    # Check for invalid formats (SQL Injection, XSS, improper IDs)
    if not is_valid_objectid(user_id) or re.search(r"['\";<>()]", user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Fetch user from DB
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 1, "name": 1, "email": 1, "created_at": 1})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Authorization: Users can only access their own profiles (unless admin)
    if current_user["role"] != "admin" and str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=403, detail=ERROR_403_FORBIDDEN_ACCESS_MESSAGE)

    # Convert MongoDB ObjectId to string and return response
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at", datetime.now(timezone.utc).isoformat())
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request, 
    user_id: str, 
    user_update: UserUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Updates a user's details with authentication, validation, and security checks.
    
    - Requires authentication.
    - Users can only update their profile (unless admin).
    - Validates ObjectId format.
    - Ensures email uniqueness and secure password hashing.
    - Prevents SQL injection & XSS.
    """

    # Rate limiting check
    await rate_limit_check(request)

    # Trim user ID and validate
    user_id = user_id.strip()
    if not is_valid_objectid(user_id) or re.search(r"['\";<>()]", user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Fetch user from DB
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)

    # Authorization: Users can only update their own profile (unless admin)
    if current_user["role"] != "admin" and str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=403, detail=ERROR_403_FORBIDDEN_ACCESS_MESSAGE)

    update_data = {}

    # Validate and update name
    if user_update.name is not None:
        if user_update.name.strip() == "":
            raise HTTPException(status_code=422, detail="Name must contain characters")
        if len(user_update.name) > 255:
            raise HTTPException(status_code=422, detail="Name cannot exceed 255 characters")
        if re.search(r"['\";<>()]", user_update.name):  # Prevent XSS and SQL Injection
            raise HTTPException(status_code=400, detail="Invalid characters in name")
        update_data["name"] = user_update.name.strip()

    # Validate and update email (ensure uniqueness)
    if user_update.email is not None:
        existing_email = await db.users.find_one({"email": user_update.email})
        if existing_email and str(existing_email["_id"]) != user_id:
            raise HTTPException(status_code=400, detail=ERROR_400_EMAIL_EXISTS_MESSAGE)
        update_data["email"] = user_update.email.lower()  # Normalize email

    # Validate and update password (secure hashing)
    if user_update.password is not None:
        if len(user_update.password) < 6:
            raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
        update_data["password"] = hash_password(user_update.password)

    # Validate and update role (admin-only)
    if user_update.role is not None:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Forbidden: Cannot change role")
        update_data["role"] = user_update.role.strip()

    # Update timestamp
    update_data["updated"] = datetime.now(timezone.utc)

    # Apply update
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)

    # Fetch updated user
    updated_user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})  # Exclude password
    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        created_at=updated_user.get("created_at", datetime.now(timezone.utc).isoformat()),
    )

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user by ID."""
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)
    return {"message": "User deleted successfully"}
