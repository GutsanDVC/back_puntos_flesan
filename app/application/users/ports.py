"""Puertos (interfaces) para la capa de aplicación de usuarios"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.users.entities import User


class UserRepositoryPort(ABC):
    """Puerto para repositorio de usuarios"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza un usuario"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario"""
        pass
    
    @abstractmethod
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Lista usuarios con filtros opcionales"""
        pass
    
    @abstractmethod
    async def count_users(
        self,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Cuenta usuarios con filtros opcionales"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con el email dado"""
        pass


class EmailServicePort(ABC):
    """Puerto para servicio de email"""
    
    @abstractmethod
    async def send_welcome_email(self, user: User) -> bool:
        """Envía email de bienvenida"""
        pass
    
    @abstractmethod
    async def send_user_deactivated_email(self, user: User) -> bool:
        """Envía email de desactivación"""
        pass


class AuditServicePort(ABC):
    """Puerto para servicio de auditoría"""
    
    @abstractmethod
    async def log_user_created(self, user: User, created_by: UUID) -> None:
        """Registra creación de usuario"""
        pass
    
    @abstractmethod
    async def log_user_updated(self, user: User, updated_by: UUID) -> None:
        """Registra actualización de usuario"""
        pass
    
    @abstractmethod
    async def log_user_deactivated(self, user: User, deactivated_by: UUID) -> None:
        """Registra desactivación de usuario"""
        pass
    
    @abstractmethod
    async def log_role_assigned(self, user: User, role: str, assigned_by: UUID) -> None:
        """Registra asignación de rol"""
        pass
