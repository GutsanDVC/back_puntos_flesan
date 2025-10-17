"""Modelo SQLAlchemy para User"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.session import Base


class UserModel(Base):
    """Modelo SQLAlchemy para User"""
    
    __tablename__ = "users"
    __table_args__ = {"schema": "puntos_flesan"}
    
    # ID primario automático
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4,
        comment="ID primario automático"
    )
    
    # ID del usuario del datawarehouse (pendiente implementación)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Número identificatorio del datawarehouse (pendiente implementación)"
    )
    
    # Información básica del usuario
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="Email del usuario"
    )
    first_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Nombre del usuario"
    )
    last_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Apellido del usuario"
    )
    
    # Puntos disponibles
    puntos_disponibles: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Puntos disponibles para canjear"
    )
    
    # Rol del usuario (un solo rol por usuario)
    rol: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        index=True,
        comment="Rol del usuario (USER, USER_LEADER, MANAGER, ADMIN)"
    )
    
    # Permisos (JSON array de permisos calculados según el rol)
    permisos: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="JSON array de permisos calculados según el rol"
    )
    
    # Estado y fechas
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Usuario activo"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Fecha de última actualización"
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Fecha de último login"
    )
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email}')>"
