"""Autenticación de desarrollo - Solo para testing"""

from uuid import UUID, uuid4
from app.core.config import settings
from app.core.security import CurrentUser, Role, Permission


def get_dev_user() -> CurrentUser:
    """Crea un usuario de desarrollo con permisos de administrador"""
    from app.core.security import get_permissions_for_roles
    
    admin_permissions = get_permissions_for_roles([Role.ADMIN])
    
    return CurrentUser(
        id="12345678-1234-5678-9012-123456789012",
        user_id=999999,  # ID ficticio del datawarehouse
        email="dev@flesan.com",
        first_name="Usuario",
        last_name="Desarrollo",
        puntos_disponibles=1000,  # Puntos para testing
        rol=Role.ADMIN,
        permissions=admin_permissions,
        is_active=True
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
