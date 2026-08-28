from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "bhoomiflow-api"
    }

@router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    try:
        # Execute basic query to verify connection
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )
