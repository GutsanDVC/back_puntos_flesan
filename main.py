"""Punto de entrada principal de la aplicación FastAPI"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import setup_logging
from app.core.database import create_tables

# Routers (arquitectura por capas)
from app.api.routers import (
    user_router,
    health_router,
    beneficio_router,
    canje_router
)
# TODO: Restaurar o migrar servicios de datawarehouse y colaboradores
# from app.api.routers import datawarehouse_router, colaboradores_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    setup_logging()
    await create_tables()
    yield
    # Shutdown
    pass


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend con FastAPI - Arquitectura por Capas (Layered)",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
if settings.CORS_ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )

# Middleware de seguridad
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En producción, especificar hosts permitidos
)

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Registrar routers
app.include_router(health_router)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(beneficio_router, prefix=settings.API_V1_PREFIX)
app.include_router(canje_router, prefix=settings.API_V1_PREFIX)
# TODO: Restaurar o migrar servicios de datawarehouse y colaboradores
# app.include_router(datawarehouse_router, prefix=settings.API_V1_PREFIX)
# app.include_router(colaboradores_router, prefix=settings.API_V1_PREFIX)

# Endpoint raíz
@app.get("/")
async def read_root():
    print("🚀 CORS_ALLOWED_ORIGINS:", settings.CORS_ALLOWED_ORIGINS)
    """Endpoint raíz de la API"""
    return {
        "message": "FastAPI Backend Template funcionando correctamente",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health/"
    }
