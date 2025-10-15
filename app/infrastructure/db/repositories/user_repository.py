"""Implementación del repositorio de usuarios usando SQLAlchemy"""

import json
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.users.ports import UserRepositoryPort
from app.core.security import Role
from app.domain.users.entities import User
from app.infrastructure.db.models import UserModel


class SQLAlchemyUserRepository(UserRepositoryPort):
    """Implementación SQLAlchemy del repositorio de usuarios"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario"""
        user_model = self._to_model(user)
        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)
        return self._to_entity(user_model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por ID"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._to_entity(user_model)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return self._to_entity(user_model)
        return None
    
    async def update(self, user: User) -> User:
        """Actualiza un usuario"""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one()
        
        # Actualizar campos
        user_model.email = user.email
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.roles = json.dumps([role.value for role in user.roles])
        user_model.is_active = user.is_active
        user_model.updated_at = user.updated_at
        user_model.last_login = user.last_login
        
        await self.session.flush()
        await self.session.refresh(user_model)
        return self._to_entity(user_model)
    
    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario (soft delete - marca como inactivo)"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model:
            user_model.is_active = False
            await self.session.flush()
            return True
        return False
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Lista usuarios con filtros opcionales"""
        stmt = select(UserModel)
        
        # Aplicar filtros
        conditions = []
        if email:
            conditions.append(UserModel.email.ilike(f"%{email}%"))
        if is_active is not None:
            conditions.append(UserModel.is_active == is_active)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Aplicar paginación y ordenamiento
        stmt = stmt.order_by(UserModel.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._to_entity(model) for model in user_models]
    
    async def count_users(
        self,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Cuenta usuarios con filtros opcionales"""
        stmt = select(func.count(UserModel.id))
        
        # Aplicar filtros
        conditions = []
        if email:
            conditions.append(UserModel.email.ilike(f"%{email}%"))
        if is_active is not None:
            conditions.append(UserModel.is_active == is_active)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con el email dado"""
        stmt = select(func.count(UserModel.id)).where(UserModel.email == email.lower())
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0
    
    def _to_entity(self, model: UserModel) -> User:
        """Convierte modelo SQLAlchemy a entidad de dominio"""
        roles_data = json.loads(model.roles)
        roles = [Role(role) for role in roles_data]
        
        return User(
            id=model.id,
            email=model.email,
            first_name=model.first_name,
            last_name=model.last_name,
            roles=roles,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    def _to_model(self, entity: User) -> UserModel:
        """Convierte entidad de dominio a modelo SQLAlchemy"""
        return UserModel(
            id=entity.id,
            email=entity.email,
            first_name=entity.first_name,
            last_name=entity.last_name,
            roles=json.dumps([role.value for role in entity.roles]),
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login=entity.last_login
        )
