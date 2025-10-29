"""Esquemas Pydantic para validación de canjes de puntos"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CanjeCreateRequest(BaseModel):
    """Esquema para crear un canje de puntos"""
    user_id: int = Field(..., gt=0, description="ID del usuario del datawarehouse")
    beneficio_id: UUID = Field(..., description="ID del beneficio a canjear (UUID)")
    puntos_utilizar: int = Field(..., gt=0, description="Cantidad de puntos a utilizar")
    fecha_canje: datetime = Field(..., description="Fecha en que se realiza el canje")
    fecha_uso: datetime = Field(..., description="Fecha programada para usar el beneficio")
    jornada: Optional[str] = Field(None, min_length=1, max_length=50, description="Jornada del beneficio (requerida solo si el beneficio lo exige)")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")
    
    @field_validator('fecha_uso')
    @classmethod
    def validate_fecha_uso(cls, v, info):
        """Valida que la fecha de uso sea posterior a la fecha de canje"""
        if 'fecha_canje' in info.data and v <= info.data['fecha_canje']:
            raise ValueError('La fecha de uso debe ser posterior a la fecha de canje')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 6070,
                "beneficio_id": "8f3d0a8c-9a5b-4c2e-9b1e-1a2b3c4d5e6f",
                "puntos_utilizar": 100,
                "fecha_canje": "2025-01-24T10:00:00",
                "fecha_uso": "2025-02-01T10:00:00",
                "jornada": "COMPLETA",
                "observaciones": "Canje para día libre"
            }
        }


class CanjeResponse(BaseModel):
    """Esquema de respuesta para un canje"""
    id: UUID
    user_id: int
    beneficio_id: UUID
    puntos_canjeados: int
    fecha_canje: datetime
    fecha_uso: datetime
    jornada: Optional[str] = None
    estado: str
    observaciones: Optional[str] = None
    puntos_restantes: int  # Puntos que le quedan al usuario después del canje
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CanjeListResponse(BaseModel):
    """Esquema de respuesta para lista de canjes"""
    canjes: List[CanjeResponse]
    total: int
    page: int
    size: int
    total_pages: int


class CanjeEstadoUpdate(BaseModel):
    """Esquema para actualizar el estado de un canje"""
    estado: str = Field(..., pattern="^(ACTIVO|USADO|CANCELADO|VENCIDO)$")
    observaciones: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "estado": "USADO",
                "observaciones": "Beneficio utilizado correctamente"
            }
        }
