from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.core.config import settings
from app.core.database import create_tables
from app.api.endpoints import router
from app.api.patient_history_endpoints import router as history_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered personalized patient discharge instructions system",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Include API routes
app.include_router(router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting AI Discharge Instructions API...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise
    
    # Check OpenRouter API key
    if not settings.openrouter_api_key:
        logger.warning("OpenRouter API key not configured. AI features will not work.")
    else:
        logger.info("OpenRouter API key configured successfully")
    
    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Shutting down AI Discharge Instructions API...")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Discharge Instructions API",
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs" if settings.debug else "Documentation disabled in production"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
