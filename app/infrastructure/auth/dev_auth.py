"""Autenticación de desarrollo - Solo para testing"""

from uuid import UUID, uuid4
from app.core.config import settings
from app.core.security import CurrentUser, Role, Permission


def get_dev_user() -> CurrentUser:
    """Crea un usuario de desarrollo con permisos de administrador"""
    return CurrentUser(
        user_id="12345678-1234-5678-9012-123456789012",
        email="dev@flesan.com",
        roles=[Role.ADMIN, Role.MANAGER, Role.USER],
        is_active=True,
        permissions={Permission.ADMIN, Permission.READ, Permission.WRITE, Permission.DELETE}
    )


async def get_dev_current_user() -> CurrentUser:
    """Dependency que retorna usuario de desarrollo"""
    if settings.ENVIRONMENT != "development":
        raise Exception("Usuario de desarrollo solo disponible en modo development")
    
    return get_dev_user()


# Funciones de bypass para desarrollo
async def dev_require_admin() -> CurrentUser:
    """Bypass de require_admin para desarrollo"""
    return await get_dev_current_user()


async def dev_require_manager_or_admin() -> CurrentUser:
    """Bypass de require_manager_or_admin para desarrollo"""
    return await get_dev_current_user()


async def dev_get_current_user() -> CurrentUser:
    """Bypass de get_current_user para desarrollo"""
    return await get_dev_current_user()
