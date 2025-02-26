from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, HTTPException
from slowapi.errors import RateLimitExceeded
import os

# Disable rate limiting in tests
if os.getenv("TEST_ENV") == "true":
    limiter = Limiter(key_func=get_remote_address, enabled=False)  # ✅ Rate limit disabled in test mode
else:
    limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])  # ✅ Rate limit enabled normally

# Custom exception handler for 429 Too Many Requests
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handles 429 Too Many Requests errors."""
    raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
