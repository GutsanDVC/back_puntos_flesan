"""Puertos (interfaces) para la aplicación de beneficios"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from app.domain.beneficios.entities.beneficio import Beneficio


class BeneficioRepositoryPort(ABC):
    """Puerto para repositorio de beneficios"""
    
    @abstractmethod
    async def create(self, beneficio: Beneficio) -> Beneficio:
        """Crea un nuevo beneficio"""
        pass
    
    @abstractmethod
    async def get_by_id(self, beneficio_id: UUID) -> Optional[Beneficio]:
        """Obtiene un beneficio por ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Beneficio]:
        """Obtiene un beneficio por nombre"""
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        page: int = 1, 
        size: int = 10,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Beneficio], int]:
        """Lista beneficios con paginación"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        page: int = 1, 
        size: int = 10
    ) -> Tuple[List[Beneficio], int]:
        """Busca beneficios por texto"""
        pass
    
    @abstractmethod
    async def update(self, beneficio: Beneficio) -> Beneficio:
        """Actualiza un beneficio"""
        pass
    
    @abstractmethod
    async def delete(self, beneficio_id: UUID) -> bool:
        """Elimina un beneficio"""
        pass
    
    @abstractmethod
    async def get_active_beneficios(self) -> List[Beneficio]:
        """Obtiene beneficios activos"""
        pass
