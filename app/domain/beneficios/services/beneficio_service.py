"""Servicio de dominio para Beneficios"""

from typing import List, Optional
from uuid import UUID

from app.domain.beneficios.entities.beneficio import Beneficio


class BeneficioService:
    """Servicio de dominio para lógica de negocio de beneficios"""
    
    @staticmethod
    def validate_beneficio_name_uniqueness(
        beneficios: List[Beneficio], 
        new_name: str, 
        exclude_id: Optional[UUID] = None
    ) -> bool:
        """Valida que el nombre del beneficio sea único"""
        for beneficio in beneficios:
            if exclude_id and beneficio.id == exclude_id:
                continue
            if beneficio.beneficio.lower() == new_name.lower():
                return False
        return True
    
    @staticmethod
    def calculate_total_value(beneficios: List[Beneficio]) -> int:
        """Calcula el valor total de todos los beneficios activos"""
        return sum(b.valor for b in beneficios if b.is_active)
    
    @staticmethod
    def filter_active_beneficios(beneficios: List[Beneficio]) -> List[Beneficio]:
        """Filtra solo los beneficios activos"""
        return [b for b in beneficios if b.is_active]
    
    @staticmethod
    def sort_by_value(beneficios: List[Beneficio], descending: bool = True) -> List[Beneficio]:
        """Ordena beneficios por valor"""
        return sorted(beneficios, key=lambda b: b.valor, reverse=descending)
