"""Punto de entrada principal de la aplicación FastAPI"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logger import setup_logging
from app.infrastructure.db import create_tables
from app.interfaces.api import users_router, health_router


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
    description="Template de backend con FastAPI siguiendo Arquitectura Limpia",
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
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )

# Middleware de seguridad
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # En producción, especificar hosts permitidos
)

# Registrar routers
app.include_router(health_router)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)

# Endpoint raíz
@app.get("/")
async def read_root():
    """Endpoint raíz de la API"""
    return {
        "message": "FastAPI Backend Template funcionando correctamente",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health/"
    }
