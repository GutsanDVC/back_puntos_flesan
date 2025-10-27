"""Esquemas Pydantic para validación de entrada/salida"""

from app.api.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse
)
from app.api.schemas.beneficio_schema import (
    BeneficioCreateRequest,
    BeneficioUpdateRequest,
    BeneficioResponse,
    BeneficioListResponse,
    BeneficioSummaryResponse
)

__all__ = [
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserResponse",
    "UserListResponse",
    "BeneficioCreateRequest",
    "BeneficioUpdateRequest",
    "BeneficioResponse",
    "BeneficioListResponse",
    "BeneficioSummaryResponse"
]
