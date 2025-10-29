"""Esquemas Pydantic para validación de beneficios"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BeneficioCreateRequest(BaseModel):
    """Esquema para crear beneficio"""
    beneficio: str = Field(..., min_length=1, max_length=200)
    detalle: str = Field(..., min_length=1)
    valor: int = Field(..., ge=0, description="Valor en puntos")
    requiresJourney: bool = Field(..., description="Indica si el beneficio requiere jornada específica")

    class Config:
        json_schema_extra = {
            "example": {
                "beneficio": "Día Cambio de Casa",
                "detalle": "Un día libre para tu cambio de casa",
                "valor": 350
            }
        }


class BeneficioUpdateRequest(BaseModel):
    """Esquema para actualizar beneficio"""
    imagen: Optional[str] = Field(None, max_length=500)
    beneficio: Optional[str] = Field(None, min_length=1, max_length=200)
    detalle: Optional[str] = Field(None, min_length=1)
    valor: Optional[int] = Field(None, ge=0)
    requiresJourney: Optional[bool] = Field(None, description="Indica si el beneficio requiere jornada específica")


class BeneficioResponse(BaseModel):
    """Esquema de respuesta para beneficio"""
    id: UUID
    imagen: str
    beneficio: str
    detalle: str
    valor: int
    requiresJourney: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BeneficioListResponse(BaseModel):
    """Esquema de respuesta para lista de beneficios"""
    beneficios: List[BeneficioResponse]
    total: int
    page: int
    size: int
    total_pages: int


class BeneficioSummaryResponse(BaseModel):
    """Esquema de respuesta para resumen de beneficios"""
    total_beneficios: int
    beneficios_activos: int
    valor_total: int
