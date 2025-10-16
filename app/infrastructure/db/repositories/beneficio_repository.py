"""Repositorio para Beneficios"""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.application.beneficios.ports import BeneficioRepositoryPort
from app.domain.beneficios.entities.beneficio import Beneficio
from app.infrastructure.db.models.beneficio_model import BeneficioModel


class BeneficioRepository(BeneficioRepositoryPort):
    """Repositorio para operaciones de base de datos de beneficios"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, beneficio: Beneficio) -> Beneficio:
        """Crea un nuevo beneficio"""
        model = BeneficioModel(
            id=beneficio.id,
            imagen=beneficio.imagen,
            beneficio=beneficio.beneficio,
            detalle=beneficio.detalle,
            regla1=beneficio.regla1,
            regla2=beneficio.regla2,
            valor=beneficio.valor,
            is_active=beneficio.is_active,
            created_at=beneficio.created_at,
            updated_at=beneficio.updated_at
        )
        
        self.session.add(model)
        await self.session.flush()
        
        return self._model_to_entity(model)
    
    async def get_by_id(self, beneficio_id: UUID) -> Optional[Beneficio]:
        """Obtiene un beneficio por ID"""
        stmt = select(BeneficioModel).where(BeneficioModel.id == beneficio_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_name(self, name: str) -> Optional[Beneficio]:
        """Obtiene un beneficio por nombre"""
        stmt = select(BeneficioModel).where(
            func.lower(BeneficioModel.beneficio) == name.lower()
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def list_all(
        self, 
        page: int = 1, 
        size: int = 10, 
        is_active: Optional[bool] = None
    ) -> tuple[List[Beneficio], int]:
        """Lista beneficios con paginación y filtros"""
        # Construir query base
        stmt = select(BeneficioModel)
        
        # Aplicar filtros
        if is_active is not None:
            stmt = stmt.where(BeneficioModel.is_active == is_active)
        
        # Contar total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()
        
        # Aplicar paginación y ordenamiento
        stmt = stmt.order_by(BeneficioModel.created_at.desc())
        stmt = stmt.offset((page - 1) * size).limit(size)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        beneficios = [self._model_to_entity(model) for model in models]
        
        return beneficios, total
    
    async def search(
        self, 
        query: str, 
        page: int = 1, 
        size: int = 10
    ) -> tuple[List[Beneficio], int]:
        """Busca beneficios por texto"""
        search_term = f"%{query.lower()}%"
        
        stmt = select(BeneficioModel).where(
            or_(
                func.lower(BeneficioModel.beneficio).like(search_term),
                func.lower(BeneficioModel.detalle).like(search_term),
                func.lower(BeneficioModel.regla1).like(search_term),
                func.lower(BeneficioModel.regla2).like(search_term)
            )
        )
        
        # Contar total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()
        
        # Aplicar paginación
        stmt = stmt.order_by(BeneficioModel.created_at.desc())
        stmt = stmt.offset((page - 1) * size).limit(size)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        beneficios = [self._model_to_entity(model) for model in models]
        
        return beneficios, total
    
    async def update(self, beneficio: Beneficio) -> Beneficio:
        """Actualiza un beneficio"""
        stmt = select(BeneficioModel).where(BeneficioModel.id == beneficio.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Beneficio con ID {beneficio.id} no encontrado")
        
        # Actualizar campos
        model.imagen = beneficio.imagen
        model.beneficio = beneficio.beneficio
        model.detalle = beneficio.detalle
        model.regla1 = beneficio.regla1
        model.regla2 = beneficio.regla2
        model.valor = beneficio.valor
        model.is_active = beneficio.is_active
        model.updated_at = datetime.utcnow()
        
        await self.session.flush()
        
        return self._model_to_entity(model)
    
    async def delete(self, beneficio_id: UUID) -> bool:
        """Elimina un beneficio (soft delete)"""
        stmt = select(BeneficioModel).where(BeneficioModel.id == beneficio_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        model.is_active = False
        model.updated_at = datetime.utcnow()
        
        await self.session.flush()
        return True
    
    async def get_active_beneficios(self) -> List[Beneficio]:
        """Obtiene todos los beneficios activos"""
        stmt = select(BeneficioModel).where(BeneficioModel.is_active == True)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
    
    def _model_to_entity(self, model: BeneficioModel) -> Beneficio:
        """Convierte modelo SQLAlchemy a entidad de dominio"""
        return Beneficio(
            id=model.id,
            imagen=model.imagen,
            beneficio=model.beneficio,
            detalle=model.detalle,
            regla1=model.regla1,
            regla2=model.regla2,
            valor=model.valor,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
