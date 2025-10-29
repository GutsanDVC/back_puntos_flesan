"""Servicio de negocio para usuarios - Consolida toda la lógica de aplicación"""

from math import ceil
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.core.security import Role
from app.core.utils.validation import validate_email, validate_not_empty_string
from app.repositories.user_repository import UserRepository


class UserService:
    """Servicio de negocio para operaciones de usuarios"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        roles: List[Role]
    ) -> dict:
        """
        Crea un nuevo usuario con validaciones de negocio
        
        Validaciones:
        - Email único
        - Formato de email válido
        - Nombres no vacíos
        - Al menos un rol
        """
        # Validar formato de email
        if not validate_email(email):
            raise ValidationError("Formato de email inválido")
        
        # Validar nombres
        validate_not_empty_string(first_name, "first_name")
        validate_not_empty_string(last_name, "last_name")
        
        # Validar roles
        if not roles:
            raise ValidationError("Usuario debe tener al menos un rol")
        
        # Verificar email único
        exists = await self.repository.exists_by_email(email)
        if exists:
            raise ConflictError(f"Ya existe un usuario con el email {email}")
        
        # Normalizar datos
        email = email.lower().strip()
        first_name = first_name.strip().title()
        last_name = last_name.strip().title()
        
        # Crear usuario
        user = await self.repository.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            puntos=0
        )
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> dict:
        """Obtiene un usuario por ID"""
        user = await self.repository.get_by_id(user_id)
        print(user)
        if not user:
            raise NotFoundError(f"Usuario con ID {user_id} no encontrado")
        return user
    
    async def get_user_by_email(self, email: str) -> dict:
        """Obtiene un usuario por email"""
        user = await self.repository.get_by_email(email)
        if not user:
            raise NotFoundError(f"Usuario con email {email} no encontrado")
        return user
    
    async def get_user_by_user_id(self, user_id: int) -> dict:
        """Obtiene un usuario por user_id (ID del datawarehouse)"""
        user = await self.repository.get_by_user_id(user_id)
        if not user:
            raise NotFoundError(f"Usuario con user_id {user_id} no encontrado")
        return user
    
    async def update_user(
        self,
        user_id: UUID,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> dict:
        """
        Actualiza información del usuario con validaciones
        
        Validaciones:
        - Usuario existe
        - Email único si se cambia
        - Formato de email válido si se proporciona
        - Nombres no vacíos si se proporcionan
        """
        # Verificar que usuario existe
        user = await self.get_user_by_id(user_id)
        
        # Validar email si se proporciona
        if email is not None:
            if not validate_email(email):
                raise ValidationError("Formato de email inválido")
            
            # Verificar que email sea único
            if email.lower() != user["email"]:
                exists = await self.repository.exists_by_email(email)
                if exists:
                    raise ConflictError(f"Ya existe un usuario con el email {email}")
            
            email = email.lower().strip()
        
        # Validar nombres si se proporcionan
        if first_name is not None:
            validate_not_empty_string(first_name, "first_name")
            first_name = first_name.strip().title()
        
        if last_name is not None:
            validate_not_empty_string(last_name, "last_name")
            last_name = last_name.strip().title()
        
        # Actualizar usuario
        updated_user = await self.repository.update(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        return updated_user
    
    async def deactivate_user(self, user_id: UUID) -> dict:
        """Desactiva un usuario (soft delete)"""
        # Verificar que usuario existe
        user = await self.get_user_by_id(user_id)
        
        # Desactivar
        updated_user = await self.repository.update(
            user_id=user_id,
            is_active=False
        )
        
        return updated_user
    
    async def activate_user(self, user_id: UUID) -> dict:
        """Activa un usuario"""
        # Verificar que usuario existe
        user = await self.get_user_by_id(user_id)
        
        # Activar
        updated_user = await self.repository.update(
            user_id=user_id,
            is_active=True
        )
        
        return updated_user
    
    async def assign_role(self, user_id: UUID, role: Role) -> dict:
        """Asigna un rol a un usuario"""
        # Verificar que usuario existe
        user = await self.get_user_by_id(user_id)
        
        # Obtener roles actuales
        current_roles = user["roles"]
        
        # Agregar nuevo rol si no lo tiene
        if role not in current_roles:
            current_roles.append(role)
        
        # Actualizar usuario
        updated_user = await self.repository.update(
            user_id=user_id,
            roles=current_roles
        )
        
        return updated_user
    
    async def remove_role(self, user_id: UUID, role: Role) -> dict:
        """Remueve un rol de un usuario"""
        # Verificar que usuario existe
        user = await self.get_user_by_id(user_id)
        
        # Obtener roles actuales
        current_roles = user["roles"]
        
        # Validar que no se deje sin roles
        if len(current_roles) == 1 and role in current_roles:
            raise ValidationError("No se puede dejar al usuario sin roles")
        
        # Remover rol si lo tiene
        if role in current_roles:
            current_roles.remove(role)
        
        # Actualizar usuario
        updated_user = await self.repository.update(
            user_id=user_id,
            roles=current_roles
        )
        
        return updated_user
    
    async def list_users(
        self,
        page: int = 1,
        size: int = 10,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """
        Lista usuarios con paginación y filtros
        
        Returns:
            dict con keys: users, total, page, size, total_pages
        """
        # Calcular offset
        skip = (page - 1) * size
        
        # Obtener usuarios y total
        users = await self.repository.list_users(
            skip=skip,
            limit=size,
            email=email,
            is_active=is_active
        )
        
        total = await self.repository.count_users(
            email=email,
            is_active=is_active
        )
        
        total_pages = ceil(total / size) if total > 0 else 0
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }
    
    async def search_users(
        self,
        query: str,
        page: int = 1,
        size: int = 10
    ) -> dict:
        """
        Busca usuarios por email
        
        Returns:
            dict con keys: users, total, page, size, total_pages
        """
        return await self.list_users(
            page=page,
            size=size,
            email=query
        )
    
    async def add_puntos(self, user_id: UUID, puntos: int) -> dict:
        """Agrega puntos a un usuario"""
        # Verificar que usuario existe
        user = await self.get_user_by_id(user_id)
        
        # Validar puntos positivos
        if puntos <= 0:
            raise ValidationError("Los puntos deben ser mayores a cero")
        
        # Calcular nuevos puntos
        new_puntos = user["puntos"] + puntos
        
        # Actualizar usuario
        updated_user = await self.repository.update(
            user_id=user_id,
            puntos=new_puntos
        )
        
        return updated_user
    
    async def subtract_puntos(self, user_id: UUID, puntos: int) -> dict:
        """Resta puntos a un usuario"""
        # Verificar que usuario exists
        user = await self.get_user_by_id(user_id)
        
        # Validar puntos positivos
        if puntos <= 0:
            raise ValidationError("Los puntos deben ser mayores a cero")
        
        # Validar que tiene suficientes puntos
        if user["puntos"] < puntos:
            raise ValidationError(
                f"El usuario no tiene suficientes puntos. Disponible: {user['puntos']}, Requerido: {puntos}"
            )
        
        # Calcular nuevos puntos
        new_puntos = user["puntos"] - puntos
        
        # Actualizar usuario
        updated_user = await self.repository.update(
            user_id=user_id,
            puntos=new_puntos
        )
        
        return updated_user
