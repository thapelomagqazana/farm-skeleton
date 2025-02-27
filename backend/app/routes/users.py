from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import List
from app.database import db
from app.models import UserCreate, UserUpdate, UserResponse
from app.security import hash_password, get_current_user
from bson import ObjectId
from datetime import datetime, timezone
import re
import logging

router = APIRouter()

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

# Constants for error messages
ERROR_404_MESSAGE = "User not found"
ERROR_400_EMAIL_EXISTS_MESSAGE = "Email already registered"
ERROR_403_FORBIDDEN_ACCESS_MESSAGE = "Forbidden: Access denied"
ERROR_400_INVALID_ID = "Invalid user ID format"
ERROR_403_ROLE_CHANGE = "Forbidden: Cannot change role"
ERROR_401_NOT_AUTHENTICATED = "Not authenticated"


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse, tags=["Users"], summary="Create a New User")
async def create_user(user: UserCreate):
    """
    **Creates a new user in the system.**

    - **Requires:** `name`, `email`, `password`
    - **Returns:** The created user details.
    """
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        logger.warning(f"User creation failed: Email already exists - {user.email}")
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
        logger.error(f"User creation failed for email: {user.email}")
        raise HTTPException(status_code=500, detail="User creation failed")
    
    logger.info(f"User created successfully: {user.email}")
    return UserResponse(id=str(result.inserted_id), name=user.name, email=user.email, created_at=new_user["created"].isoformat())

@router.get("/users", response_model=List[UserResponse], tags=["Users"], summary="List All Users")
async def list_users(
    request: Request, 
    current_user: dict = Depends(get_current_user),  # Requires authentication
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    limit: int = Query(10, ge=1, description="Limit per page (default: 10, max: 100)"),
):
    """
    **Fetches a paginated list of users.**
    
    - **Requires:** Admin role.
    - **Returns:** A paginated list of users.
    """
    # Cap `limit` to 100 instead of rejecting it
    if limit > 100:
        limit = 100  # Set a max limit internally
    
    # Prevent SQL Injection or Non-Numeric Queries
    if not isinstance(page, int) or not isinstance(limit, int):
        logger.warning("Invalid pagination values")
        raise HTTPException(status_code=400, detail="Invalid pagination values")
    
    # Ensure only admins can fetch all users
    if current_user["role"] != "admin":
        logger.warning(f"Unauthorized user listing attempt by: {current_user['email']}")
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

@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"], summary="Get User by ID")
# @limiter.limit("10/minute")
async def get_user(request: Request, user_id: str, current_user: dict = Depends(get_current_user)):
    """
    **Fetch a user by ID.**

    - **Requires:** Authentication.
    - **Ensures:** Users can only access their own profiles unless they are admin.
    """
    user_id = user_id.strip()  # Trim spaces

    # Check for invalid formats (SQL Injection, XSS, improper IDs)
    if not is_valid_objectid(user_id) or re.search(r"['\";<>()]", user_id):
        raise HTTPException(status_code=400, detail=ERROR_400_INVALID_ID)

    # Fetch user from DB
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 1, "name": 1, "email": 1, "created_at": 1})

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    # Authorization: Users can only access their own profiles (unless admin)
    if current_user["role"] != "admin" and str(current_user["_id"]) != user_id:
        logger.warning(f"Unauthorized access attempt by: {current_user['email']} to user: {user_id}")
        raise HTTPException(status_code=403, detail=ERROR_403_FORBIDDEN_ACCESS_MESSAGE)

    # Convert MongoDB ObjectId to string and return response
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at", datetime.now(timezone.utc).isoformat())
    )

# **Helper Functions**
def validate_user_id(user_id: str, current_user: dict):
    """Validates the user ID format."""
    if not is_valid_objectid(user_id.strip()) or re.search(r"['\";<>()]", user_id):
        logger.warning(f"Invalid User ID format: {user_id} - Requested by: {current_user['email']}")
        raise HTTPException(status_code=400, detail=ERROR_400_INVALID_ID)
    return ObjectId(user_id.strip())

def validate_name(name: str):
    """Validates the name field."""
    name = name.strip()
    if not name:
        logger.warning("Name must contain characters")
        raise HTTPException(status_code=422, detail="Name must contain characters")
    if len(name) > 255:
        logger.warning("Name cannot exceed 255 characters")
        raise HTTPException(status_code=422, detail="Name cannot exceed 255 characters")
    if re.search(r"['\";<>()]", name):
        logger.warning("Invalid characters in name")
        raise HTTPException(status_code=400, detail="Invalid characters in name")
    return name

async def validate_email(email: str, user_id: str, current_user: dict):
    """Check if email is unique and return the normalized email."""
    existing_email = await db.users.find_one({"email": email})
    if existing_email and str(existing_email["_id"]) != user_id:
        logger.warning(f"Duplicate email update attempt - Email: {email} - By: {current_user['email']}")
        raise HTTPException(status_code=400, detail="Email already registered")
    return email.lower()


def validate_password(password: str):
    """Validates and hashes the password."""
    if len(password) < 6:
        logger.warning("Password must be at least 6 characters")
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    return hash_password(password)

async def update_user_in_db(user_id: ObjectId, update_data: dict):
    """Updates user details in the database and returns the updated user."""
    update_data["updated"] = datetime.now(timezone.utc)
    result = await db.users.update_one({"_id": user_id}, {"$set": update_data})

    if result.matched_count == 0:
        logger.warning(ERROR_404_MESSAGE)
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)

    return await db.users.find_one({"_id": user_id}, {"password": 0})  # Exclude password

@router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"], summary="Update User Details")
async def update_user(
    request: Request, 
    user_id: str, 
    user_update: UserUpdate, 
    current_user: dict = Depends(get_current_user)
):
    """
    **Updates user details.**
    
    - **Requires:** Authentication.
    - **Ensures:** Users can only update their own profiles unless admin.
    """

    user_id = validate_user_id(user_id, current_user)

    user = await db.users.find_one({"_id": user_id})
    if not user:
        logger.warning(f"User not found: {user_id} - Requested by: {current_user['email']}")
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)

    if current_user["role"] != "admin" and str(current_user["_id"]) != str(user_id):
        logger.warning(f"Unauthorized user update attempt - Target: {user_id} - By: {current_user['email']}")
        raise HTTPException(status_code=403, detail=ERROR_403_FORBIDDEN_ACCESS_MESSAGE)

    update_data = {}
    if user_update.name:
        update_data["name"] = validate_name(user_update.name)

    if user_update.email:
        update_data["email"] = await validate_email(user_update.email, str(user_id), current_user)


    if user_update.password:
        update_data["password"] = validate_password(user_update.password)

    if user_update.role:
        if current_user["role"] != "admin":
            logger.warning(f"Unauthorized role change attempt - User: {current_user['email']} tried changing {user_id}'s role")
            raise HTTPException(status_code=403, detail=ERROR_403_ROLE_CHANGE)
        update_data["role"] = user_update.role.strip()

    updated_user = await update_user_in_db(user_id, update_data)

    logger.info(f"User updated successfully - User: {updated_user['email']} (ID: {user_id}) - Updated by: {current_user['email']}")

    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        created_at=updated_user.get("created_at", datetime.now(timezone.utc).isoformat()),
    )

@router.delete("/users/{user_id}", tags=["Users"], summary="Delete a User")
async def delete_user(
    request: Request, 
    user_id: str, 
    current_user: dict = Depends(get_current_user)  # Authenticated user
):
    """
    **Deletes a user account.**
    
    - **Requires:** Admin role or the user being deleted.
    - **Returns:** Confirmation message.
    """

    user_id = user_id.strip()  # Trim spaces

    # **Security: Validate user_id format**
    if not is_valid_objectid(user_id) or re.search(r"['\";<>()]", user_id):
        logger.warning(f"Invalid User ID format: {user_id} - Requested by: {current_user['email']}")
        raise HTTPException(status_code=400, detail=ERROR_400_INVALID_ID)

    # **Fetch user from DB**
    user_to_delete = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user_to_delete:
        logger.warning(f"User not found: {user_id} - Requested by: {current_user['email']}")
        raise HTTPException(status_code=404, detail=ERROR_404_MESSAGE)

    # **Authorization: Only allow user to delete self or admin to delete any user**
    if current_user["role"] != "admin" and str(current_user["_id"]) != user_id:
        logger.warning(f"Unauthorized user deletion attempt - Target: {user_id} - By: {current_user['email']}")
        raise HTTPException(status_code=403, detail=ERROR_403_FORBIDDEN_ACCESS_MESSAGE)

    # **Delete user from DB**
    result = await db.users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        logger.error(f"User deletion failed - User ID: {user_id} - Requested by: {current_user['email']}")
        raise HTTPException(status_code=500, detail="User deletion failed")
    
    logger.info(f"User deleted successfully - User ID: {user_id} - Deleted by: {current_user['email']}")
    return {"message": "User deleted successfully"}