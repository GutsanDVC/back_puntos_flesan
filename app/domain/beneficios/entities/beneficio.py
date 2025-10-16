"""Entidad de dominio Beneficio - Pura, sin dependencias de framework"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Beneficio:
    """Entidad de dominio para Beneficio"""
    
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
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.beneficio or not self.beneficio.strip():
            raise ValueError("El nombre del beneficio es requerido")
        
        if not self.detalle or not self.detalle.strip():
            raise ValueError("El detalle del beneficio es requerido")
        
        if not self.regla1 or not self.regla1.strip():
            raise ValueError("La regla 1 es requerida")
        
        if not self.regla2 or not self.regla2.strip():
            raise ValueError("La regla 2 es requerida")
        
        if self.valor < 0:
            raise ValueError("El valor del beneficio no puede ser negativo")
    
    def activate(self) -> None:
        """Activa el beneficio"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Desactiva el beneficio"""
        self.is_active = False
    
    def update_image(self, new_image: str) -> None:
        """Actualiza la imagen del beneficio"""
        if not new_image or not new_image.strip():
            raise ValueError("La imagen no puede estar vacía")
        self.imagen = new_image
    
    def update_value(self, new_value: int) -> None:
        """Actualiza el valor del beneficio"""
        if new_value < 0:
            raise ValueError("El valor del beneficio no puede ser negativo")
        self.valor = new_value
