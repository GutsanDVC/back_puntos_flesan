"""Queries para la aplicación de beneficios"""

import math
from dataclasses import dataclass
from typing import List
from uuid import UUID

from app.application.beneficios.dto import BeneficioFilterDTO
from app.application.beneficios.ports import BeneficioRepositoryPort
from app.core.exceptions import BaseAppException
from app.domain.beneficios.entities.beneficio import Beneficio


@dataclass
class BeneficioListResult:
    """Resultado de lista de beneficios"""
    beneficios: List[Beneficio]
    total: int
    page: int
    size: int
    total_pages: int


class GetBeneficioQuery:
    """Query para obtener beneficio por ID"""
    
    def __init__(self, repository: BeneficioRepositoryPort):
        self.repository = repository
    
    async def execute(self, beneficio_id: UUID) -> Beneficio:
        """Ejecuta la consulta de beneficio por ID"""
        try:
            beneficio = await self.repository.get_by_id(beneficio_id)
            if not beneficio:
                raise BaseAppException(
                    message=f"Beneficio con ID {beneficio_id} no encontrado",
                    error_code="BENEFICIO-ERR-004",
                    details={"beneficio_id": str(beneficio_id)}
                )
            
            return beneficio
            
        except BaseAppException:
            raise
        except Exception as e:
            raise BaseAppException(
                message="Error interno al obtener beneficio",
                error_code="BENEFICIO-ERR-007",
                details={"internal_error": str(e)}
            )


class ListBeneficiosQuery:
    """Query para listar beneficios"""
    
    def __init__(self, repository: BeneficioRepositoryPort):
        self.repository = repository
    
    async def execute(self, filters: BeneficioFilterDTO) -> BeneficioListResult:
        """Ejecuta la consulta de lista de beneficios"""
        try:
            beneficios, total = await self.repository.list_all(
                page=filters.page,
                size=filters.size,
                is_active=filters.is_active
            )
            
            total_pages = math.ceil(total / filters.size) if total > 0 else 0
            
            return BeneficioListResult(
                beneficios=beneficios,
                total=total,
                page=filters.page,
                size=filters.size,
                total_pages=total_pages
            )
            
        except Exception as e:
            raise BaseAppException(
                message="Error interno al listar beneficios",
                error_code="BENEFICIO-ERR-008",
                details={"internal_error": str(e)}
            )


class SearchBeneficiosQuery:
    """Query para buscar beneficios"""
    
    def __init__(self, repository: BeneficioRepositoryPort):
        self.repository = repository
    
    async def execute(self, query: str, page: int = 1, size: int = 10) -> BeneficioListResult:
        """Ejecuta la búsqueda de beneficios"""
        try:
            if not query or len(query.strip()) < 2:
                raise BaseAppException(
                    message="El término de búsqueda debe tener al menos 2 caracteres",
                    error_code="BENEFICIO-ERR-009",
                    details={"query": query}
                )
            
            beneficios, total = await self.repository.search(
                query=query.strip(),
                page=page,
                size=size
            )
            
            total_pages = math.ceil(total / size) if total > 0 else 0
            
            return BeneficioListResult(
                beneficios=beneficios,
                total=total,
                page=page,
                size=size,
                total_pages=total_pages
            )
            
        except BaseAppException:
            raise
        except Exception as e:
            raise BaseAppException(
                message="Error interno al buscar beneficios",
                error_code="BENEFICIO-ERR-010",
                details={"internal_error": str(e)}
            )
