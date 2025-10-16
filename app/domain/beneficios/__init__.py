"""Módulo de dominio para Beneficios"""

from .entities.beneficio import Beneficio
from .services.beneficio_service import BeneficioService

__all__ = ["Beneficio", "BeneficioService"]
