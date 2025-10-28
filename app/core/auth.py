"""Funciones de autenticación y autorización"""

from typing import Optional, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import CurrentUser, Role, ROLE_PERMISSIONS
from fastapi import Request
from app.core.logger import get_logger

security = HTTPBearer(auto_error=False)
logger = get_logger(__name__)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request=None
) -> CurrentUser:
    """
    Obtiene el usuario actual desde el token JWT
    
    En modo desarrollo, permite bypass sin token para testing.
    En producción, requiere token válido.
    """

    # Bypass de autenticación en desarrollo (solo para testing)
    if settings.ENVIRONMENT == "development" and credentials is None:
        # Usuario de desarrollo por defecto
        return CurrentUser(
            id="dev-user-uuid-12345",
            user_id=None,  # ID del datawarehouse (opcional)
            email="dev@flesan.com",
            first_name="Dev",
            last_name="User",
            puntos_disponibles=0,
            rol=Role.ADMIN,
            permissions=ROLE_PERMISSIONS[Role.ADMIN],
            is_active=True
        )
    logger.debug(
            {"Token": request.cookies.get("user_token"),
            "Secret": settings.SECRET_KEY,
            "Algorithm": settings.ALGORITHM
            }
        )
    # Validación de token en producción o cuando se proporciona
    # if credentials is None:
    #     logger.warning(
    #         "Authentication failed: missing bearer credentials",
    #         extra={"extra_data": {"path": request.url.path if request else None, "reason": "missing_credentials"}}
    #     )
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="No se proporcionó token de autenticación",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    if request is None:
        logger.error(
            "Authentication failed: request object not provided",
            extra={"extra_data": {"reason": "missing_request"}}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        token = request.cookies.get("user_token")
        masked_token = None
        if token:
            masked_token = token[:8] + "..." if len(token) > 8 else token
        logger.debug(
            "Authentication cookie retrieved",
            extra={
                "extra_data": {
                    "path": request.url.path,
                    "has_token": bool(token),
                    "masked_token": masked_token,
                    "client_ip": request.client.host if request.client else None,
                }
            }
        )
        if not token:
            logger.warning(
                "Authentication failed: missing user_token cookie",
                extra={
                    "extra_data": {
                        "path": request.url.path,
                        "reason": "missing_cookie",
                        "client_ip": request.client.host if request.client else None,
                    }
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se encontró cookie de autenticación 'user_token'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")  # 
        email: str = payload.get("email")
        rol_str: str = payload.get("rol", "user")
        
        if user_id is None or email is None:
            raise AuthenticationError("Token inválido")
        
        # Convertir string de rol a enum Role
        try:
            rol = Role(rol_str.lower())
        except ValueError:
            rol = Role.USER  # Rol por defecto si no es válido
        
        # Obtener permisos según el rol
        permissions = ROLE_PERMISSIONS.get(rol, set())
        
        return CurrentUser(
            id=user_id,
            user_id=payload.get("user_id"),  # ID del datawarehouse
            email=email,
            first_name=payload.get("first_name", ""),
            last_name=payload.get("last_name", ""),
            puntos_disponibles=payload.get("puntos_disponibles", 0),
            rol=rol,
            permissions=permissions,
            is_active=payload.get("is_active", True)
        )
        
    except JWTError as exc:
        logger.error(
            "Authentication failed: invalid or expired token",
            extra={
                "extra_data": {
                    "path": request.url.path if request else None,
                    "reason": "invalid_token",
                    "client_ip": request.client.host if request and request.client else None,
                }
            },
            exc_info=exc
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Requiere que el usuario tenga rol ADMIN
    """
    if current_user.rol != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


async def require_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Requiere que el usuario esté activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


# === Autorización basada en permisos (no por rol) ===
def require_permission(permission: str) -> Callable[..., CurrentUser]:
    """Crea una dependencia que exige un permiso específico.
    
    - Verifica que el permiso esté presente en `current_user.permissions`.
    - Lanza 403 si no lo tiene.
    """
    async def _dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permission}"
            )
        return current_user
    return _dependency


# Dependencias concretas por permiso solicitado
require_redeem_points = require_permission("redeem_points")
require_view_own_points = require_permission("view_own_points")
require_view_own_history = require_permission("view_own_history")
require_view_benefits = require_permission("view_benefits")
require_view_team_points = require_permission("view_team_points")
require_view_team_history = require_permission("view_team_history")
require_view_company_history = require_permission("view_company_history")
require_manage_benefits = require_permission("manage_benefits")
require_give_extra_points = require_permission("give_extra_points")
require_create_users = require_permission("create_users")
require_create_managers = require_permission("create_managers")
require_system_config = require_permission("system_config")
