"""Router para endpoints de health check"""

from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.db import get_db
from app.interfaces.api.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica el estado de salud de la aplicación y sus dependencias",
    responses={
        200: {"description": "Servicio saludable"},
        503: {"description": "Servicio no disponible"}
    }
)
async def health_check(
    db: AsyncSession = Depends(get_db)
) -> HealthResponse:
    """Endpoint de health check"""
    
    # Verificar conexión a base de datos
    database_status = "connected"
    try:
        # Ejecutar una query simple para verificar la conexión
        await db.execute("SELECT 1")
    except Exception:
        database_status = "disconnected"
    
    return HealthResponse(
        status="healthy" if database_status == "connected" else "unhealthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        database=database_status
    )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Verifica si la aplicación está lista para recibir tráfico",
    responses={
        200: {"description": "Aplicación lista"},
        503: {"description": "Aplicación no lista"}
    }
)
async def readiness_check() -> dict:
    """Endpoint de readiness check para Kubernetes"""
    return {"status": "ready", "timestamp": datetime.utcnow()}


@router.get(
    "/live",
    summary="Liveness Check", 
    description="Verifica si la aplicación está viva",
    responses={
        200: {"description": "Aplicación viva"},
        503: {"description": "Aplicación no responde"}
    }
)
async def liveness_check() -> dict:
    """Endpoint de liveness check para Kubernetes"""
    return {"status": "alive", "timestamp": datetime.utcnow()}
