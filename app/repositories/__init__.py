"""Capa de acceso a datos - Repositorios con SQL RAW"""

from app.repositories.user_repository import UserRepository
from app.repositories.beneficio_repository import BeneficioRepository

__all__ = ["UserRepository", "BeneficioRepository"]
