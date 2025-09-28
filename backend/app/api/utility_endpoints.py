from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db, engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/db-health")
async def check_db_health(db: Session = Depends(get_db)):
    """Check database connection health"""
    try:
        # Test raw connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Test ORM session
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy", 
            "database": str(engine.url),
            "orm": "working"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )

@router.get("/app-status")
async def app_status():
    """Check application status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "service": "AI Discharge Instructions"
    }
