"""Dependencias de autenticación para FastAPI"""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import CurrentUser, Role, Permission, get_permissions_for_roles
from app.infrastructure.auth.jwks_client import jwt_validator
from app.infrastructure.auth.dev_auth import get_dev_user

security = HTTPBearer(auto_error=False)


async def get_token_from_cookie(
    session_cookie: Optional[str] = Cookie(None, alias=settings.COOKIE_NAME)
) -> Optional[str]:
    """Extrae el token de la cookie de sesión"""
    return session_cookie


async def get_current_user(
    token: Optional[str] = Depends(get_token_from_cookie)
) -> CurrentUser:
    """Obtiene el usuario actual desde el token JWT"""
    
    # 🧪 MODO DESARROLLO: Usar usuario mock
    if settings.ENVIRONMENT == "development":
        return get_dev_user()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Validar token JWT
        payload = await jwt_validator.validate_token(token)
        
        # Extraer información del usuario
        user_id = payload.get("sub")
        email = payload.get("email")
        roles_claim = payload.get("roles", [])
        
        if not user_id or not email:
            raise AuthenticationError("Token inválido: falta información del usuario")
        
        # Convertir roles
        try:
            roles = [Role(role) for role in roles_claim if role in [r.value for r in Role]]
        except ValueError as e:
            raise AuthenticationError(f"Roles inválidos en token: {e}")
        
        # Obtener permisos basados en roles
        permissions = get_permissions_for_roles(roles)
        
        # Por ahora usar el primer rol como rol principal
        # TODO: Actualizar cuando se implemente la lógica de usuario único
        primary_role = roles[0] if roles else Role.USER
        
        return CurrentUser(
            id=user_id,
            user_id=None,  # TODO: Obtener del datawarehouse
            email=email,
            first_name="Usuario",  # TODO: Obtener del token o BD
            last_name="JWT",  # TODO: Obtener del token o BD
            puntos_disponibles=0,  # TODO: Obtener de la BD
            rol=primary_role,
            permissions=permissions,
            is_active=True
        )
        
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error procesando autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_current_user(
    token: Optional[str] = Depends(get_token_from_cookie)
) -> Optional[CurrentUser]:
    """Obtiene el usuario actual de forma opcional (puede ser None)"""
    
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


def require_roles(*required_roles: Role):
    """Dependency factory para requerir roles específicos"""
    
    def check_roles(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.rol not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los roles: {[r.value for r in required_roles]}"
            )
        return current_user
    
    return check_roles


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency para requerir rol de administrador"""
    # 🧪 MODO DESARROLLO: El usuario mock ya tiene permisos de admin
    if settings.ENVIRONMENT == "development":
        return current_user
    
    if current_user.rol != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return current_user


def require_manager_or_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency para requerir rol de manager o admin"""
    # 🧪 MODO DESARROLLO: El usuario mock ya tiene permisos de manager y admin
    if settings.ENVIRONMENT == "development":
        return current_user
    
    if current_user.rol not in [Role.ADMIN, Role.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de manager o administrador"
        )
    return current_user


def require_leader_or_above(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Dependency para requerir rol de leader o superior"""
    # 🧪 MODO DESARROLLO: El usuario mock ya tiene permisos
    if settings.ENVIRONMENT == "development":
        return current_user
    
    if current_user.rol not in [Role.ADMIN, Role.MANAGER, Role.USER_LEADER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de leader, manager o administrador"
        )
    return current_user


def require_permission(permission: Permission):
    """Factory para crear dependency que requiere un permiso específico"""
    def check_permission(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        # 🧪 MODO DESARROLLO: El usuario mock ya tiene todos los permisos
        if settings.ENVIRONMENT == "development":
            return current_user
        
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere el permiso: {permission.value}"
            )
        return current_user
    
    return check_permission


async def validate_session_token(token: str) -> bool:
    """Valida si un token de sesión es válido"""
    try:
        await jwt_validator.validate_token(token)
        return True
    except AuthenticationError:
        return False
