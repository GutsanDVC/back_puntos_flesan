"""DTOs para la aplicación de beneficios"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateBeneficioDTO:
    """DTO para crear beneficio"""
    beneficio: str
    detalle: str
    regla1: str
    regla2: str
    valor: int
    imagen: Optional[str] = None  # Se asignará después de subir el archivo


@dataclass
class UpdateBeneficioDTO:
    """DTO para actualizar beneficio"""
    imagen: Optional[str] = None
    beneficio: Optional[str] = None
    detalle: Optional[str] = None
    regla1: Optional[str] = None
    regla2: Optional[str] = None
    valor: Optional[int] = None


@dataclass
class BeneficioFilterDTO:
    """DTO para filtros de beneficios"""
    page: int = 1
    size: int = 10
    is_active: Optional[bool] = None
