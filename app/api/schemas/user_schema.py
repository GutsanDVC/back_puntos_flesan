"""Esquemas Pydantic para validación de usuarios"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.security import Role


class UserCreateRequest(BaseModel):
    """Esquema para crear usuario"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: Role = Field(default=Role.USER)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": "USER"
            }
        }


class UserUpdateRequest(BaseModel):
    """Esquema para actualizar usuario"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[Role] = None


class UserResponse(BaseModel):
    """Esquema de respuesta para usuario"""
    id: UUID
    user_id: Optional[int] = None  # ID del datawarehouse
    email: str
    first_name: str
    last_name: str
    full_name: str
    role: Role
    permissions: List[str]
    puntos: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Esquema de respuesta para lista de usuarios"""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    total_pages: int
