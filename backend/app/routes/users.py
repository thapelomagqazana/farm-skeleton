"""
User-related API routes for CRUD operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.database import db
from app.models import UserCreate, UserUpdate, UserInDB
from app.security import hash_password
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

ERROR_404_MESSAGE = "User not found"
ERROR_400_EMAIL_EXISTS_MESSAGE = "Email already registered"

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user with hashed password.

    :param user: UserCreate schema.
    :return: ID of the newly created user.
    """
    existing_user = await db.users.find_one({"email": user.email})
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
    return {"id": str(result.inserted_id)}

@router.get("/users", response_model=list[UserInDB])
async def list_users():
    """Retrieve a list of all users."""
    users = await db.users.find().to_list(100)
    return [{"name": u["name"], "email": u["email"], "created": u["created"], "updated": u["updated"]} for u in users]

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
