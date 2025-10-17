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
    USER_LEADER = "user_leader"
    MANAGER = "manager"


class Permission(str, Enum):
    """Permisos disponibles en el sistema"""
    # Permisos de puntos
    REDEEM_POINTS = "redeem_points"
    VIEW_OWN_POINTS = "view_own_points"
    VIEW_OWN_HISTORY = "view_own_history"
    VIEW_TEAM_POINTS = "view_team_points"
    VIEW_TEAM_HISTORY = "view_team_history"
    GIVE_EXTRA_POINTS = "give_extra_points"
    
    # Permisos de beneficios
    VIEW_BENEFITS = "view_benefits"
    MANAGE_BENEFITS = "manage_benefits"
    
    # Permisos de usuarios
    CREATE_USERS = "create_users"
    CREATE_MANAGERS = "create_managers"
    
    # Permisos de empresa
    VIEW_COMPANY_HISTORY = "view_company_history"
    
    # Permisos de configuración
    SYSTEM_CONFIG = "system_config"


class CurrentUser(BaseModel):
    """Modelo para el usuario actual autenticado"""
    id: str  # UUID del usuario
    user_id: Optional[int] = None  # ID del datawarehouse
    email: str
    first_name: str
    last_name: str
    puntos_disponibles: int = 0
    rol: Role  # Un solo rol
    permissions: Set[Permission]
    is_active: bool = True
    
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role: Role) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return self.rol == role
    
    def has_permission(self, permission: Permission) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        return permission in self.permissions
    
    def has_any_role(self, roles: List[Role]) -> bool:
        """Verifica si el usuario tiene alguno de los roles especificados"""
        return self.rol in roles
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Verifica si el usuario tiene todos los permisos especificados"""
        return all(permission in self.permissions for permission in permissions)
    
    def can_manage_user(self, target_user_role: Role) -> bool:
        """Verifica si puede gestionar un usuario con el rol especificado"""
        if self.rol == Role.ADMIN:
            return True  # Admin puede gestionar todos
        elif self.rol == Role.MANAGER:
            return target_user_role in [Role.USER, Role.USER_LEADER]  # Manager puede gestionar USER y USER_LEADER
        elif self.rol == Role.USER_LEADER:
            return target_user_role == Role.USER  # Leader solo puede ver USER
        return False


# Mapeo de roles a permisos
ROLE_PERMISSIONS = {
    Role.USER: {
        Permission.REDEEM_POINTS,
        Permission.VIEW_OWN_POINTS,
        Permission.VIEW_OWN_HISTORY,
        Permission.VIEW_BENEFITS
    },
    Role.USER_LEADER: {
        # Permisos de USER +
        Permission.REDEEM_POINTS,
        Permission.VIEW_OWN_POINTS,
        Permission.VIEW_OWN_HISTORY,
        Permission.VIEW_BENEFITS,
        # Permisos adicionales de LEADER
        Permission.VIEW_TEAM_POINTS,
        Permission.VIEW_TEAM_HISTORY
    },
    Role.MANAGER: {
        # Permisos de USER_LEADER +
        Permission.REDEEM_POINTS,
        Permission.VIEW_OWN_POINTS,
        Permission.VIEW_OWN_HISTORY,
        Permission.VIEW_BENEFITS,
        Permission.VIEW_TEAM_POINTS,
        Permission.VIEW_TEAM_HISTORY,
        # Permisos adicionales de MANAGER
        Permission.VIEW_COMPANY_HISTORY,
        Permission.MANAGE_BENEFITS,
        Permission.GIVE_EXTRA_POINTS,
        Permission.CREATE_USERS
    },
    Role.ADMIN: {
        # Todos los permisos anteriores +
        Permission.REDEEM_POINTS,
        Permission.VIEW_OWN_POINTS,
        Permission.VIEW_OWN_HISTORY,
        Permission.VIEW_BENEFITS,
        Permission.VIEW_TEAM_POINTS,
        Permission.VIEW_TEAM_HISTORY,
        Permission.VIEW_COMPANY_HISTORY,
        Permission.MANAGE_BENEFITS,
        Permission.GIVE_EXTRA_POINTS,
        Permission.CREATE_USERS,
        # Permisos exclusivos de ADMIN
        Permission.CREATE_MANAGERS,
        Permission.SYSTEM_CONFIG
    }
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
