import logging
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from app.routes import users, auth
from app.security import get_current_user
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Get values from .env
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

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

# Initialize FastAPI App with Swagger Metadata
app = FastAPI(
    title="FARM Skeleton Backend",
    description="A backend API for user authentication and management with FastAPI.",
    version="1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # Redoc UI
    openapi_url="/openapi.json"  # OpenAPI JSON spec
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # Read from .env
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Attach Routes
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests."""
    start_time = datetime.now(timezone.utc)
    response = await call_next(request)
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    logger.info(
        f"Request: {request.method} {request.url} | Status: {response.status_code} | Duration: {duration:.2f}s"
    )
    return response

@app.get("/", tags=["General"])
async def home():
    """Root endpoint of the API.
    
    Returns:
        A welcome message.
    """
    logger.info("Home endpoint accessed")
    return {"message": "Welcome to the FARM Skeleton Backend"}

# Custom OpenAPI Schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FARM Skeleton Backend API",
        version="1.0",
        description="A backend service for authentication and user management.",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
