"""Servicios de dominio para User - Lógica de negocio pura"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import BusinessRuleException, ValidationError
from app.core.security import Role
from app.core.utils.validation import validate_email, validate_not_empty_string
from app.domain.users.entities import User


class UserDomainService:
    """Servicio de dominio para operaciones complejas de usuarios"""
    
    @staticmethod
    def create_user(
        email: str,
        first_name: str,
        last_name: str,
        roles: List[Role],
        user_id: Optional[UUID] = None
    ) -> User:
        """Crea un nuevo usuario con validaciones de dominio"""
        
        # Validaciones de entrada
        if not validate_email(email):
            raise ValidationError("Formato de email inválido")
        
        validate_not_empty_string(first_name, "first_name")
        validate_not_empty_string(last_name, "last_name")
        
        if not roles:
            raise ValidationError("Usuario debe tener al menos un rol")
        
        # Normalizar datos
        email = email.lower().strip()
        first_name = first_name.strip().title()
        last_name = last_name.strip().title()
        
        # Crear entidad
        return User(
            id=user_id or UUID(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            is_active=True,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def can_assign_role(user: User, new_role: Role, assigner_roles: List[Role]) -> bool:
        """Verifica si un usuario puede asignar un rol a otro"""
        
        # Solo admins pueden asignar rol de admin
        if new_role == Role.ADMIN and Role.ADMIN not in assigner_roles:
            return False
        
        # Managers pueden asignar roles de user y viewer
        if Role.MANAGER in assigner_roles:
            return new_role in [Role.USER, Role.VIEWER]
        
        # Admins pueden asignar cualquier rol
        if Role.ADMIN in assigner_roles:
            return True
        
        return False
    
    @staticmethod
    def validate_role_assignment(
        user: User, 
        new_role: Role, 
        assigner_roles: List[Role]
    ) -> None:
        """Valida que se pueda asignar un rol"""
        
        if not UserDomainService.can_assign_role(user, new_role, assigner_roles):
            raise BusinessRuleException(
                f"No tienes permisos para asignar el rol {new_role.value}",
                details={
                    "user_id": str(user.id),
                    "new_role": new_role.value,
                    "assigner_roles": [r.value for r in assigner_roles]
                }
            )
    
    @staticmethod
    def can_deactivate_user(user: User, deactivator_roles: List[Role]) -> bool:
        """Verifica si un usuario puede desactivar a otro"""
        
        # No se puede desactivar a un admin a menos que seas admin
        if Role.ADMIN in user.roles and Role.ADMIN not in deactivator_roles:
            return False
        
        # Managers y admins pueden desactivar usuarios normales
        return any(role in deactivator_roles for role in [Role.ADMIN, Role.MANAGER])
    
    @staticmethod
    def validate_user_deactivation(
        user: User, 
        deactivator_roles: List[Role]
    ) -> None:
        """Valida que se pueda desactivar un usuario"""
        
        if not UserDomainService.can_deactivate_user(user, deactivator_roles):
            raise BusinessRuleException(
                "No tienes permisos para desactivar este usuario",
                details={
                    "user_id": str(user.id),
                    "user_roles": [r.value for r in user.roles],
                    "deactivator_roles": [r.value for r in deactivator_roles]
                }
            )
    
    @staticmethod
    def update_user_info(
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> User:
        """Actualiza información del usuario con validaciones"""
        
        if email is not None:
            if not validate_email(email):
                raise ValidationError("Formato de email inválido")
            user.email = email.lower().strip()
        
        if first_name is not None:
            validate_not_empty_string(first_name, "first_name")
            user.first_name = first_name.strip().title()
        
        if last_name is not None:
            validate_not_empty_string(last_name, "last_name")
            user.last_name = last_name.strip().title()
        
        user.updated_at = datetime.utcnow()
        return user
