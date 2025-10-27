"""Routers de la API organizados por módulo"""

from app.api.routers.user_router import router as user_router
from app.api.routers.health_router import router as health_router
from app.api.routers.beneficio_router import router as beneficio_router
from app.api.routers.canje_router import router as canje_router

# TODO: Restaurar cuando se migren servicios de datawarehouse
# from app.api.routers.datawarehouse_router import router as datawarehouse_router
# from app.api.routers.colaboradores_router import router as colaboradores_router

__all__ = [
    "user_router",
    "health_router",
    "beneficio_router",
    "canje_router"
    # "datawarehouse_router",
    # "colaboradores_router"
]
