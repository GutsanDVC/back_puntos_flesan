"""Entidad de dominio User - Pura, sin dependencias de framework"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.security import Role


@dataclass
class User:
    """Entidad de dominio para Usuario"""
    
    id: UUID
    email: str
    first_name: str
    last_name: str
    roles: List[Role]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.email or '@' not in self.email:
            raise ValueError("Email inválido")
        
        if not self.first_name or not self.first_name.strip():
            raise ValueError("Nombre es requerido")
        
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Apellido es requerido")
        
        if not self.roles:
            raise ValueError("Usuario debe tener al menos un rol")
    
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role: Role) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        return role in self.roles
    
    def add_role(self, role: Role) -> None:
        """Agrega un rol al usuario"""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role: Role) -> None:
        """Remueve un rol del usuario"""
        if role in self.roles:
            self.roles.remove(role)
    
    def activate(self) -> None:
        """Activa el usuario"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Desactiva el usuario"""
        self.is_active = False
    
    def update_last_login(self, login_time: datetime) -> None:
        """Actualiza la fecha del último login"""
        self.last_login = login_time
