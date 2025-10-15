"""Sistema de permisos y autorización"""

from functools import wraps
from typing import Callable, List

from fastapi import HTTPException, status

from app.core.security import CurrentUser, Permission, Role


class PermissionChecker:
    """Verificador de permisos"""
    
    @staticmethod
    def has_permission(user: CurrentUser, permission: Permission) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        return permission in user.permissions
    
    @staticmethod
    def has_any_permission(user: CurrentUser, permissions: List[Permission]) -> bool:
        """Verifica si el usuario tiene alguno de los permisos especificados"""
        return any(permission in user.permissions for permission in permissions)
    
    @staticmethod
    def has_all_permissions(user: CurrentUser, permissions: List[Permission]) -> bool:
        """Verifica si el usuario tiene todos los permisos especificados"""
        return all(permission in user.permissions for permission in permissions)
    
    @staticmethod
    def can_access_resource(user: CurrentUser, resource_owner_id: str) -> bool:
        """Verifica si el usuario puede acceder a un recurso específico"""
        # Los admins pueden acceder a cualquier recurso
        if Role.ADMIN in user.roles:
            return True
        
        # Los usuarios solo pueden acceder a sus propios recursos
        return user.user_id == resource_owner_id
    
    @staticmethod
    def can_modify_user(current_user: CurrentUser, target_user_roles: List[Role]) -> bool:
        """Verifica si el usuario actual puede modificar a otro usuario"""
        # Los admins pueden modificar a cualquiera
        if Role.ADMIN in current_user.roles:
            return True
        
        # Los managers pueden modificar usuarios normales, pero no admins
        if Role.MANAGER in current_user.roles:
            return Role.ADMIN not in target_user_roles
        
        return False


def require_permission(permission: Permission):
    """Decorador para requerir un permiso específico"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar current_user en los argumentos
            current_user = None
            for arg in args:
                if isinstance(arg, CurrentUser):
                    current_user = arg
                    break
            
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if not PermissionChecker.has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere el permiso: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """Decorador para requerir cualquiera de los permisos especificados"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar current_user en los argumentos
            current_user = None
            for arg in args:
                if isinstance(arg, CurrentUser):
                    current_user = arg
                    break
            
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if not PermissionChecker.has_any_permission(current_user, permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere uno de los permisos: {[p.value for p in permissions]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_resource_access(resource_owner_id_param: str = "user_id"):
    """Decorador para verificar acceso a recursos específicos"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar current_user en los argumentos
            current_user = None
            for arg in args:
                if isinstance(arg, CurrentUser):
                    current_user = arg
                    break
            
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Obtener ID del propietario del recurso
            resource_owner_id = kwargs.get(resource_owner_id_param)
            if not resource_owner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Parámetro {resource_owner_id_param} requerido"
                )
            
            if not PermissionChecker.can_access_resource(current_user, str(resource_owner_id)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para acceder a este recurso"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Instancia global del verificador de permisos
permission_checker = PermissionChecker()
