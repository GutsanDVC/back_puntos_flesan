"""Punto de entrada principal de la aplicación FastAPI"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.core.config import settings
from app.core.logger import setup_logging
from app.core.database import create_tables

import sys
from pathlib import Path
# BASE_DIR: /var/www/fastapi/api_puntos_flesan/back_puntos_flesan
BASE_DIR = Path(__file__).resolve().parent
# PROJECT_ROOT: /var/www/fastapi/api_puntos_flesan
PROJECT_ROOT = BASE_DIR.parent

# Agrega ambos niveles al PYTHONPATH si no están
for path in (BASE_DIR, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.append(path_str)

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

# Manejo personalizado de errores de validación
CUSTOM_FIELD_MESSAGES = {
    "beneficio_id": "Debes seleccionar un beneficio antes de realizar el canje.",
    "user_id": "Debes indicar el usuario que realizará el canje.",
    "puntos_utilizar": "Debes especificar la cantidad de puntos a utilizar en el canje.",
}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Personaliza el mensaje de error cuando faltan campos obligatorios"""
    errores = []

    for error in exc.errors():
        loc = [str(item) for item in error.get("loc", []) if item not in {"body", "__root__"}]
        field = loc[-1] if loc else ""

        if error.get("type") == "missing" and field:
            message = CUSTOM_FIELD_MESSAGES.get(
                field,
                f"El campo '{field}' es obligatorio."
            )
        else:
            message = error.get("msg", "Error de validación en la solicitud.")

        errores.append(
            {
                "field": field or "",
                "message": message,
                "detail": error
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "message": "La solicitud contiene datos inválidos.",
            "errors": errores
        }
    )

# Registrar routers
app.include_router(health_router)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(beneficio_router, prefix=settings.API_V1_PREFIX)
app.include_router(canje_router, prefix=settings.API_V1_PREFIX)
# TODO: Restaurar o migrar servicios de datawarehouse y colaboradores
# app.include_router(datawarehouse_router, prefix=settings.API_V1_PREFIX)
# app.include_router(colaboradores_router, prefix=settings.API_V1_PREFIX)

# Endpoint raíz

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": app.title, "version": app.version},
    )
