"""Queries (casos de uso de lectura) para usuarios"""

from typing import List, Optional
from uuid import UUID

from app.application.users.dto import UserResponseDTO, UserListResponseDTO, UserFilterDTO
from app.application.users.ports import UserRepositoryPort
from app.core.exceptions import NotFoundError
from app.domain.users.entities import User


class GetUserQuery:
    """Query para obtener un usuario por ID"""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository
    
    async def execute(self, user_id: UUID) -> UserResponseDTO:
        """Ejecuta la consulta de usuario"""
        
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"Usuario con ID {user_id} no encontrado")
        
        return self._to_response_dto(user)
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )


class GetUserByEmailQuery:
    """Query para obtener un usuario por email"""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository
    
    async def execute(self, email: str) -> UserResponseDTO:
        """Ejecuta la consulta de usuario por email"""
        
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundError(f"Usuario con email {email} no encontrado")
        
        return self._to_response_dto(user)
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )


class ListUsersQuery:
    """Query para listar usuarios con filtros y paginación"""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository
    
    async def execute(self, filters: UserFilterDTO) -> UserListResponseDTO:
        """Ejecuta la consulta de lista de usuarios"""
        
        # Calcular offset para paginación
        skip = (filters.page - 1) * filters.size
        
        # Obtener usuarios
        users = await self.user_repository.list_users(
            skip=skip,
            limit=filters.size,
            email=filters.email,
            is_active=filters.is_active
        )
        
        # Contar total
        total = await self.user_repository.count_users(
            email=filters.email,
            is_active=filters.is_active
        )
        
        # Calcular total de páginas
        total_pages = (total + filters.size - 1) // filters.size
        
        # Convertir a DTOs
        user_dtos = [self._to_response_dto(user) for user in users]
        
        return UserListResponseDTO(
            users=user_dtos,
            total=total,
            page=filters.page,
            size=filters.size,
            total_pages=total_pages
        )
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )


class SearchUsersQuery:
    """Query para buscar usuarios por texto"""
    
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository
    
    async def execute(
        self, 
        search_term: str, 
        page: int = 1, 
        size: int = 10
    ) -> UserListResponseDTO:
        """Ejecuta la búsqueda de usuarios"""
        
        # Calcular offset para paginación
        skip = (page - 1) * size
        
        # Buscar en email, nombre y apellido
        users = []
        total = 0
        
        # Buscar por email
        if "@" in search_term:
            email_users = await self.user_repository.list_users(
                skip=skip,
                limit=size,
                email=search_term
            )
            users.extend(email_users)
            total += await self.user_repository.count_users(email=search_term)
        else:
            # Buscar por nombre (implementación simplificada)
            # En una implementación real, esto sería más sofisticado
            all_users = await self.user_repository.list_users(skip=0, limit=1000)
            filtered_users = [
                user for user in all_users
                if search_term.lower() in user.first_name.lower() 
                or search_term.lower() in user.last_name.lower()
                or search_term.lower() in user.full_name.lower()
            ]
            
            total = len(filtered_users)
            users = filtered_users[skip:skip + size]
        
        # Calcular total de páginas
        total_pages = (total + size - 1) // size
        
        # Convertir a DTOs
        user_dtos = [self._to_response_dto(user) for user in users]
        
        return UserListResponseDTO(
            users=user_dtos,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
