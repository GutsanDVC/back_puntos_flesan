"""Esquemas Pydantic para la API de usuarios"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.security import Role


class UserCreateRequest(BaseModel):
    """Esquema para crear usuario"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    last_name: str = Field(..., min_length=1, max_length=100, description="Apellido del usuario")
    roles: List[Role] = Field(..., description="Roles del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez",
                "roles": ["user"]
            }
        }


class UserUpdateRequest(BaseModel):
    """Esquema para actualizar usuario"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del usuario")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Apellido del usuario")
    email: Optional[EmailStr] = Field(None, description="Email del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Juan Carlos",
                "last_name": "Pérez González",
                "email": "nuevo.email@ejemplo.com"
            }
        }


class AssignRoleRequest(BaseModel):
    """Esquema para asignar rol"""
    role: Role = Field(..., description="Rol a asignar")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "manager"
            }
        }


class UserResponse(BaseModel):
    """Esquema de respuesta para usuario"""
    id: UUID
    email: str
    first_name: str
    last_name: str
    full_name: str
    roles: List[Role]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez",
                "full_name": "Juan Pérez",
                "roles": ["user"],
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": None,
                "last_login": None
            }
        }


class UserListResponse(BaseModel):
    """Esquema de respuesta para lista de usuarios"""
    users: List[UserResponse]
    total: int = Field(..., description="Total de usuarios")
    page: int = Field(..., description="Página actual")
    size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Total de páginas")

    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "usuario@ejemplo.com",
                        "first_name": "Juan",
                        "last_name": "Pérez",
                        "full_name": "Juan Pérez",
                        "roles": ["user"],
                        "is_active": True,
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": None,
                        "last_login": None
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10,
                "total_pages": 1
            }
        }


class ErrorResponse(BaseModel):
    """Esquema de respuesta para errores"""
    message: str = Field(..., description="Mensaje de error")
    error_code: str = Field(..., description="Código de error")
    details: Optional[dict] = Field(None, description="Detalles adicionales del error")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Usuario no encontrado",
                "error_code": "APP-ERR-006",
                "details": {"user_id": "123e4567-e89b-12d3-a456-426614174000"}
            }
        }


class HealthResponse(BaseModel):
    """Esquema de respuesta para health check"""
    status: str = Field(..., description="Estado del servicio")
    timestamp: datetime = Field(..., description="Timestamp del check")
    version: str = Field(..., description="Versión de la aplicación")
    database: str = Field(..., description="Estado de la base de datos")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2023-01-01T00:00:00Z",
                "version": "1.0.0",
                "database": "connected"
            }
        }
