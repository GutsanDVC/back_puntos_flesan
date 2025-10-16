"""Esquemas Pydantic para la API de beneficios"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class BeneficioCreateRequest(BaseModel):
    """Esquema para crear beneficio (sin imagen, se maneja por separado)"""
    beneficio: str = Field(..., min_length=1, max_length=200, description="Nombre del beneficio")
    detalle: str = Field(..., min_length=1, description="Descripción detallada del beneficio")
    regla1: str = Field(..., min_length=1, max_length=200, description="Primera regla del beneficio")
    regla2: str = Field(..., min_length=1, max_length=200, description="Segunda regla del beneficio")
    valor: int = Field(..., ge=0, description="Valor en puntos del beneficio")

    class Config:
        json_schema_extra = {
            "example": {
                "beneficio": "Día Cambio de Casa",
                "detalle": "Un día libre para tu cambio de casa",
                "regla1": "1 Vez por año",
                "regla2": "1 Vez por mes",
                "valor": 350
            }
        }


class BeneficioUpdateRequest(BaseModel):
    """Esquema para actualizar beneficio"""
    imagen: Optional[str] = Field(None, min_length=1, max_length=500, description="URL o ruta de la imagen del beneficio")
    beneficio: Optional[str] = Field(None, min_length=1, max_length=200, description="Nombre del beneficio")
    detalle: Optional[str] = Field(None, min_length=1, description="Descripción detallada del beneficio")
    regla1: Optional[str] = Field(None, min_length=1, max_length=200, description="Primera regla del beneficio")
    regla2: Optional[str] = Field(None, min_length=1, max_length=200, description="Segunda regla del beneficio")
    valor: Optional[int] = Field(None, ge=0, description="Valor en puntos del beneficio")

    class Config:
        json_schema_extra = {
            "example": {
                "imagen": "host/media/beneficios/CambiodeCasa.png",
                "beneficio": "Día Cambio de Casa Actualizado",
                "detalle": "Un día libre para tu cambio de casa con nuevas condiciones",
                "regla1": "2 Veces por año",
                "regla2": "1 Vez por mes",
                "valor": 400
            }
        }


class BeneficioResponse(BaseModel):
    """Esquema de respuesta para beneficio"""
    id: UUID
    imagen: str
    beneficio: str
    detalle: str
    regla1: str
    regla2: str
    valor: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "imagen": "host/media/beneficios/CambiodeCasa.png",
                "beneficio": "Día Cambio de Casa",
                "detalle": "Un día libre para tu cambio de casa",
                "regla1": "1 Vez por año",
                "regla2": "1 Vez por mes",
                "valor": 350,
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": None
            }
        }


class BeneficioListResponse(BaseModel):
    """Esquema de respuesta para lista de beneficios"""
    beneficios: List[BeneficioResponse]
    total: int = Field(..., description="Total de beneficios")
    page: int = Field(..., description="Página actual")
    size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Total de páginas")

    class Config:
        json_schema_extra = {
            "example": {
                "beneficios": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "imagen": "host/media/beneficios/CambiodeCasa.png",
                        "beneficio": "Día Cambio de Casa",
                        "detalle": "Un día libre para tu cambio de casa",
                        "regla1": "1 Vez por año",
                        "regla2": "1 Vez por mes",
                        "valor": 350,
                        "is_active": True,
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": None
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10,
                "total_pages": 1
            }
        }


class BeneficioSummaryResponse(BaseModel):
    """Esquema de respuesta para resumen de beneficios"""
    total_beneficios: int = Field(..., description="Total de beneficios")
    beneficios_activos: int = Field(..., description="Beneficios activos")
    valor_total: int = Field(..., description="Valor total de todos los beneficios activos")

    class Config:
        json_schema_extra = {
            "example": {
                "total_beneficios": 10,
                "beneficios_activos": 8,
                "valor_total": 2800
            }
        }
