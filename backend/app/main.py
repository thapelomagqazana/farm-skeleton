"""
Main entry point for FastAPI application.
"""

from fastapi import FastAPI
from app.routes import users, auth

app = FastAPI(title="FARM Skeleton Backend", version="1.0")

# Include user and authentication routes
app.include_router(users.router, prefix="/api")
app.include_router(auth.router, prefix="/auth")

@app.get("/")
def home():
    """Root endpoint."""
    return {"message": "Welcome to the FARM Skeleton Backend"}
