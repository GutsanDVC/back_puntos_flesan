"""Configuración de seguridad, roles y permisos"""

from enum import Enum
from functools import wraps
from typing import List, Optional, Set

from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.exceptions import AuthorizationError


class Role(str, Enum):
    """Roles disponibles en el sistema"""
    ADMIN = "admin"
    USER = "user"
    MANAGER = "manager"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permisos disponibles en el sistema"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class CurrentUser(BaseModel):
    """Modelo para el usuario actual autenticado"""
    user_id: str
    email: str
    roles: List[Role]
    permissions: Set[Permission]
    is_active: bool = True
    
    def has_role(self, role: Role) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return role in self.roles
    
    def has_permission(self, permission: Permission) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        return permission in self.permissions
    
    def has_any_role(self, roles: List[Role]) -> bool:
        """Verifica si el usuario tiene alguno de los roles especificados"""
        return any(role in self.roles for role in roles)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Verifica si el usuario tiene todos los permisos especificados"""
        return all(permission in self.permissions for permission in permissions)


# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN},
    Role.MANAGER: {Permission.READ, Permission.WRITE},
    Role.USER: {Permission.READ, Permission.WRITE},
    Role.VIEWER: {Permission.READ},
}


def get_permissions_for_roles(roles: List[Role]) -> Set[Permission]:
    """Obtiene todos los permisos para una lista de roles"""
    permissions = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, set()))
    return permissions


def requires_role(required_role: Role):
    """Decorador para requerir un rol específico"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener current_user de los kwargs
            current_user = kwargs.get('current_user')
            if not current_user or not isinstance(current_user, CurrentUser):
                raise AuthorizationError("Usuario no autenticado")
            
            if not current_user.has_role(required_role):
                raise AuthorizationError(
                    f"Se requiere el rol {required_role.value}",
                    details={"required_role": required_role.value, "user_roles": [r.value for r in current_user.roles]}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def requires_permission(required_permission: Permission):
    """Decorador para requerir un permiso específico"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener current_user de los kwargs
            current_user = kwargs.get('current_user')
            if not current_user or not isinstance(current_user, CurrentUser):
                raise AuthorizationError("Usuario no autenticado")
            
            if not current_user.has_permission(required_permission):
                raise AuthorizationError(
                    f"Se requiere el permiso {required_permission.value}",
                    details={"required_permission": required_permission.value, "user_permissions": list(current_user.permissions)}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def requires_any_role(required_roles: List[Role]):
    """Decorador para requerir cualquiera de los roles especificados"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or not isinstance(current_user, CurrentUser):
                raise AuthorizationError("Usuario no autenticado")
            
            if not current_user.has_any_role(required_roles):
                raise AuthorizationError(
                    f"Se requiere uno de los roles: {[r.value for r in required_roles]}",
                    details={"required_roles": [r.value for r in required_roles], "user_roles": [r.value for r in current_user.roles]}
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
