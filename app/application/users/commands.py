"""Comandos (casos de uso de escritura) para usuarios"""

from typing import List
from uuid import UUID

from app.application.users.dto import CreateUserDTO, UpdateUserDTO, UserResponseDTO, AssignRoleDTO
from app.application.users.ports import UserRepositoryPort, EmailServicePort, AuditServicePort
from app.core.exceptions import BusinessRuleException, NotFoundError
from app.core.security import Role, CurrentUser
from app.domain.users.entities import User
from app.domain.users.services import UserDomainService


class CreateUserCommand:
    """Comando para crear un usuario"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        email_service: EmailServicePort,
        audit_service: AuditServicePort
    ):
        self.user_repository = user_repository
        self.email_service = email_service
        self.audit_service = audit_service
    
    async def execute(self, dto: CreateUserDTO, current_user: CurrentUser) -> UserResponseDTO:
        """Ejecuta la creación de usuario"""
        
        # Verificar que no existe un usuario con el mismo email
        if await self.user_repository.exists_by_email(dto.email):
            raise BusinessRuleException(
                f"Ya existe un usuario con el email {dto.email}",
                details={"email": dto.email}
            )
        
        # Crear entidad de dominio
        user = UserDomainService.create_user(
            email=dto.email,
            first_name=dto.first_name,
            last_name=dto.last_name,
            roles=dto.roles
        )
        
        # Validar permisos para asignar roles
        for role in dto.roles:
            UserDomainService.validate_role_assignment(user, role, current_user.roles)
        
        # Persistir usuario
        created_user = await self.user_repository.create(user)
        
        # Enviar email de bienvenida (no bloquear si falla)
        try:
            await self.email_service.send_welcome_email(created_user)
        except Exception:
            # Log error pero no fallar la operación
            pass
        
        # Auditar acción
        await self.audit_service.log_user_created(created_user, UUID(current_user.user_id))
        
        return self._to_response_dto(created_user)
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )


class UpdateUserCommand:
    """Comando para actualizar un usuario"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        audit_service: AuditServicePort
    ):
        self.user_repository = user_repository
        self.audit_service = audit_service
    
    async def execute(
        self, 
        user_id: UUID, 
        dto: UpdateUserDTO, 
        current_user: CurrentUser
    ) -> UserResponseDTO:
        """Ejecuta la actualización de usuario"""
        
        # Obtener usuario existente
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"Usuario con ID {user_id} no encontrado")
        
        # Verificar email único si se está cambiando
        if dto.email and dto.email != user.email:
            if await self.user_repository.exists_by_email(dto.email):
                raise BusinessRuleException(
                    f"Ya existe un usuario con el email {dto.email}",
                    details={"email": dto.email}
                )
        
        # Actualizar usando servicio de dominio
        updated_user = UserDomainService.update_user_info(
            user=user,
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email
        )
        
        # Persistir cambios
        saved_user = await self.user_repository.update(updated_user)
        
        # Auditar acción
        await self.audit_service.log_user_updated(saved_user, UUID(current_user.user_id))
        
        return self._to_response_dto(saved_user)
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )


class AssignRoleCommand:
    """Comando para asignar rol a usuario"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        audit_service: AuditServicePort
    ):
        self.user_repository = user_repository
        self.audit_service = audit_service
    
    async def execute(self, dto: AssignRoleDTO, current_user: CurrentUser) -> UserResponseDTO:
        """Ejecuta la asignación de rol"""
        
        # Obtener usuario
        user = await self.user_repository.get_by_id(dto.user_id)
        if not user:
            raise NotFoundError(f"Usuario con ID {dto.user_id} no encontrado")
        
        # Validar permisos
        UserDomainService.validate_role_assignment(user, dto.role, current_user.roles)
        
        # Asignar rol
        user.add_role(dto.role)
        
        # Persistir cambios
        updated_user = await self.user_repository.update(user)
        
        # Auditar acción
        await self.audit_service.log_role_assigned(
            updated_user, 
            dto.role.value, 
            UUID(current_user.user_id)
        )
        
        return self._to_response_dto(updated_user)
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )


class DeactivateUserCommand:
    """Comando para desactivar usuario"""
    
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        email_service: EmailServicePort,
        audit_service: AuditServicePort
    ):
        self.user_repository = user_repository
        self.email_service = email_service
        self.audit_service = audit_service
    
    async def execute(self, user_id: UUID, current_user: CurrentUser) -> UserResponseDTO:
        """Ejecuta la desactivación de usuario"""
        
        # Obtener usuario
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"Usuario con ID {user_id} no encontrado")
        
        # Validar permisos
        UserDomainService.validate_user_deactivation(user, current_user.roles)
        
        # Desactivar usuario
        user.deactivate()
        
        # Persistir cambios
        updated_user = await self.user_repository.update(user)
        
        # Enviar email de notificación
        try:
            await self.email_service.send_user_deactivated_email(updated_user)
        except Exception:
            # Log error pero no fallar la operación
            pass
        
        # Auditar acción
        await self.audit_service.log_user_deactivated(
            updated_user, 
            UUID(current_user.user_id)
        )
        
        return self._to_response_dto(updated_user)
    
    def _to_response_dto(self, user: User) -> UserResponseDTO:
        """Convierte entidad a DTO de respuesta"""
        return UserResponseDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            roles=user.roles,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
