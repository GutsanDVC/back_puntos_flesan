"""Router de health check"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db


router = APIRouter(tags=["health"])


@router.get("/health/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Endpoint de health check"""
    # Verificar conexión a base de datos
    try:
        result = await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.utcnow(),
        "version": settings.VERSION,
        "database": db_status
    }
