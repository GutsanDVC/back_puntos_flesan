"""DTOs para la capa de aplicación de usuarios"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.security import Role


class CreateUserDTO(BaseModel):
    """DTO para crear un usuario"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    roles: List[Role]


class UpdateUserDTO(BaseModel):
    """DTO para actualizar un usuario"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponseDTO(BaseModel):
    """DTO de respuesta para usuario"""
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


class UserListResponseDTO(BaseModel):
    """DTO de respuesta para lista de usuarios"""
    users: List[UserResponseDTO]
    total: int
    page: int
    size: int
    total_pages: int


class AssignRoleDTO(BaseModel):
    """DTO para asignar rol a usuario"""
    user_id: UUID
    role: Role


class UserFilterDTO(BaseModel):
    """DTO para filtros de búsqueda de usuarios"""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: Optional[List[Role]] = None
    is_active: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)
