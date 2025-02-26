from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List, Optional
from app.database import db
from app.models import UserCreate, UserUpdate, UserInDB, UserResponse
from app.security import hash_password, get_current_user
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

# Constants for error messages
ERROR_404_MESSAGE = "User not found"
ERROR_400_EMAIL_EXISTS_MESSAGE = "Email already registered"

# Rate limiting setup
RATE_LIMIT_TRACKER = {}
MAX_REQUESTS = 10  # Maximum allowed requests
TIME_FRAME = 60  # 60 seconds time window

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
    current_user: str = Depends(get_current_user),  # Requires authentication
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

    # Count total users
    total_users = await db.users.count_documents({})
    if total_users == 0:
        return []

    # Fetch users with pagination
    skip = (page - 1) * limit
    users_cursor = db.users.find({}, {"_id": 1, "name": 1, "email": 1, "created_at": 1}).skip(skip).limit(limit)
    users_list = await users_cursor.to_list(length=limit)

    # Convert MongoDB `_id` to string format
    for user in users_list:
        user["id"] = str(user["_id"])
        del user["_id"]

        # Ensure `created_at` exists; fallback to a default timestamp
        if "created_at" not in user:
            user["created_at"] = datetime.now(timezone.utc).isoformat()

    return users_list

@router.get("/users/{user_id}", response_model=UserInDB)
async def get_user(user_id: str):
    """Fetch a user by ID."""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)
    return {"name": user["name"], "email": user["email"], "created": user["created"], "updated": user["updated"]}

@router.put("/users/{user_id}", response_model=UserInDB)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user details."""
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items()}
    update_data["updated"] = datetime.now(timezone.utc)
    
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)
    
    return await get_user(user_id)

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user by ID."""
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)
    return {"message": "User deleted successfully"}
