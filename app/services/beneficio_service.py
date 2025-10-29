"""Servicio de negocio para beneficios - Lógica de aplicación"""

from math import ceil
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.core.utils.validation import validate_not_empty_string
from app.repositories.beneficio_repository import BeneficioRepository


class BeneficioService:
    """Servicio de negocio para operaciones de beneficios"""
    
    def __init__(self, repository: BeneficioRepository):
        self.repository = repository
    
    async def create_beneficio(
        self,
        beneficio: str,
        detalle: str,
        valor: int,
        imagen: str,
        requiresJourney: bool
    ) -> dict:
        """
        Crea un nuevo beneficio con validaciones de negocio
        
        Validaciones:
        - Nombre único
        - Campos no vacíos
        - Valor no negativo
        """
        # Validar campos
        validate_not_empty_string(beneficio, "beneficio")
        validate_not_empty_string(detalle, "detalle")
        validate_not_empty_string(imagen, "imagen")
        
        if valor < 0:
            raise ValidationError("El valor debe ser mayor o igual a cero")
        
        # Verificar nombre único
        exists = await self.repository.get_by_name(beneficio)
        if exists:
            raise ConflictError(f"Ya existe un beneficio con el nombre '{beneficio}'")
        
        # Crear beneficio
        return await self.repository.create(
            beneficio=beneficio.strip(),
            detalle=detalle.strip(),
            valor=valor,
            imagen=imagen,
            requiresJourney=requiresJourney
        )
    
    async def get_beneficio_by_id(self, beneficio_id: UUID) -> dict:
        """Obtiene un beneficio por ID"""
        beneficio = await self.repository.get_by_id(beneficio_id)
        if not beneficio:
            raise NotFoundError(f"Beneficio con ID {beneficio_id} no encontrado")
        return beneficio
    
    async def update_beneficio(
        self,
        beneficio_id: UUID,
        imagen: Optional[str] = None,
        beneficio: Optional[str] = None,
        detalle: Optional[str] = None,
        valor: Optional[int] = None,
        requiresJourney: Optional[bool] = None
    ) -> dict:
        """
        Actualiza un beneficio con validaciones
        
        Validaciones:
        - Beneficio existe
        - Nombre único si se cambia
        - Campos no vacíos si se proporcionan
        - Valor no negativo si se proporciona
        """
        # Verificar que beneficio existe
        current = await self.get_beneficio_by_id(beneficio_id)
        
        # Validar campos si se proporcionan
        if beneficio is not None:
            validate_not_empty_string(beneficio, "beneficio")
            beneficio = beneficio.strip()
            
            # Verificar nombre único si cambió
            if beneficio.lower() != current["beneficio"].lower():
                exists = await self.repository.get_by_name(beneficio)
                if exists:
                    raise ConflictError(f"Ya existe un beneficio con el nombre '{beneficio}'")
        
        if detalle is not None:
            validate_not_empty_string(detalle, "detalle")
            detalle = detalle.strip()
        
        if imagen is not None:
            validate_not_empty_string(imagen, "imagen")
        
        if valor is not None and valor < 0:
            raise ValidationError("El valor debe ser mayor o igual a cero")
        
        # Actualizar beneficio
        return await self.repository.update(
            beneficio_id=beneficio_id,
            imagen=imagen,
            beneficio=beneficio,
            detalle=detalle,
            valor=valor,
            requiresJourney=requiresJourney
        )
    
    async def deactivate_beneficio(self, beneficio_id: UUID) -> dict:
        """Desactiva un beneficio (soft delete)"""
        # Verificar que beneficio existe
        await self.get_beneficio_by_id(beneficio_id)
        
        # Desactivar
        return await self.repository.update(
            beneficio_id=beneficio_id,
            is_active=False
        )
    
    async def activate_beneficio(self, beneficio_id: UUID) -> dict:
        """Activa un beneficio"""
        # Verificar que beneficio existe
        await self.get_beneficio_by_id(beneficio_id)
        
        # Activar
        return await self.repository.update(
            beneficio_id=beneficio_id,
            is_active=True
        )
    
    async def list_beneficios(
        self,
        page: int = 1,
        size: int = 10,
        is_active: Optional[bool] = None
    ) -> dict:
        """
        Lista beneficios con paginación y filtros
        
        Returns:
            dict con keys: beneficios, total, page, size, total_pages
        """
        # Calcular offset
        skip = (page - 1) * size
        
        # Obtener beneficios y total
        beneficios = await self.repository.list_beneficios(
            skip=skip,
            limit=size,
            is_active=is_active
        )
        
        total = await self.repository.count_beneficios(is_active=is_active)
        total_pages = ceil(total / size) if total > 0 else 0
        
        return {
            "beneficios": beneficios,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }
    
    async def search_beneficios(
        self,
        query: str,
        page: int = 1,
        size: int = 10
    ) -> dict:
        """
        Busca beneficios por texto
        
        Returns:
            dict con keys: beneficios, total, page, size, total_pages
        """
        # Validar query
        if not query or len(query.strip()) < 2:
            raise ValidationError("La búsqueda debe tener al menos 2 caracteres")
        
        # Calcular offset
        skip = (page - 1) * size
        
        # Buscar beneficios
        beneficios = await self.repository.search(
            search_term=query,
            skip=skip,
            limit=size
        )
        
        total = await self.repository.count_search(search_term=query)
        total_pages = ceil(total / size) if total > 0 else 0
        
        return {
            "beneficios": beneficios,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }
    
    async def get_summary(self) -> dict:
        """
        Obtiene resumen estadístico de beneficios
        
        Returns:
            dict con keys: total_beneficios, beneficios_activos, valor_total
        """
        return await self.repository.get_summary()
