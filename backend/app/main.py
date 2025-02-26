"""
Main entry point for FastAPI application.
"""

from fastapi import FastAPI
# from slowapi.errors import RateLimitExceeded
# from app.utils.rate_limiter import limiter, rate_limit_exceeded_handler

app = FastAPI(title="FARM Skeleton Backend", version="1.0")

# Attach rate limiter middleware
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

from app.routes import users, auth

# Include user and authentication routes
app.include_router(users.router, prefix="/api")
app.include_router(auth.router, prefix="/auth")

@app.get("/")
def home():
    """Root endpoint."""
    return {"message": "Welcome to the FARM Skeleton Backend"}
