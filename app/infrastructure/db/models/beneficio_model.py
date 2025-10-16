"""Modelo SQLAlchemy para Beneficio"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.session import Base


class BeneficioModel(Base):
    """Modelo SQLAlchemy para Beneficio"""
    
    __tablename__ = "beneficios"
    __table_args__ = {"schema": "puntos_flesan"}
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    imagen: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        comment="URL o ruta de la imagen del beneficio"
    )
    beneficio: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        index=True,
        comment="Nombre del beneficio"
    )
    detalle: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="Descripción detallada del beneficio"
    )
    regla1: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="Primera regla del beneficio"
    )
    regla2: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="Segunda regla del beneficio"
    )
    valor: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        comment="Valor en puntos del beneficio"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False,
        comment="Estado activo del beneficio"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<BeneficioModel(id={self.id}, beneficio='{self.beneficio}', valor={self.valor})>"
