"""
Database configuration for MongoDB using Motor (AsyncIOMotorClient).
"""

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pymongo.database import Database

# Load environment variables
load_dotenv()

# Fetch MongoDB connection URI from .env file
MONGO_URI = os.getenv("MONGO_URI")

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client.farm_skeleton  # Database name

def get_database() -> Database:
    return db