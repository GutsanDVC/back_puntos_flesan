"""Dependencias para la capa de interfaces API"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.users import (
    CreateUserCommand,
    UpdateUserCommand,
    AssignRoleCommand,
    DeactivateUserCommand,
    GetUserQuery,
    GetUserByEmailQuery,
    ListUsersQuery,
    SearchUsersQuery,
    UserRepositoryPort,
    EmailServicePort,
    AuditServicePort
)
from app.application.beneficios import (
    CreateBeneficioCommand,
    UpdateBeneficioCommand,
    DeactivateBeneficioCommand,
    GetBeneficioQuery,
    ListBeneficiosQuery,
    SearchBeneficiosQuery,
    BeneficioRepositoryPort
)
from app.infrastructure.db import get_db, SQLAlchemyUserRepository, BeneficioRepository
from app.infrastructure.external import MockEmailGateway, MockAuditGateway


# Repositorios
async def get_user_repository(
    session: AsyncSession = Depends(get_db)
) -> UserRepositoryPort:
    """Dependency para obtener repositorio de usuarios"""
    return SQLAlchemyUserRepository(session)


# Servicios externos
async def get_email_service() -> EmailServicePort:
    """Dependency para obtener servicio de email"""
    # En producción, usar EmailGateway con configuración real
    return MockEmailGateway()


async def get_audit_service() -> AuditServicePort:
    """Dependency para obtener servicio de auditoría"""
    # En producción, usar AuditGateway con configuración real
    return MockAuditGateway()


# Comandos (casos de uso de escritura)
async def get_create_user_command(
    user_repository: UserRepositoryPort = Depends(get_user_repository),
    email_service: EmailServicePort = Depends(get_email_service),
    audit_service: AuditServicePort = Depends(get_audit_service)
) -> CreateUserCommand:
    """Dependency para obtener comando de crear usuario"""
    return CreateUserCommand(user_repository, email_service, audit_service)


async def get_update_user_command(
    user_repository: UserRepositoryPort = Depends(get_user_repository),
    audit_service: AuditServicePort = Depends(get_audit_service)
) -> UpdateUserCommand:
    """Dependency para obtener comando de actualizar usuario"""
    return UpdateUserCommand(user_repository, audit_service)


async def get_assign_role_command(
    user_repository: UserRepositoryPort = Depends(get_user_repository),
    audit_service: AuditServicePort = Depends(get_audit_service)
) -> AssignRoleCommand:
    """Dependency para obtener comando de asignar rol"""
    return AssignRoleCommand(user_repository, audit_service)


async def get_deactivate_user_command(
    user_repository: UserRepositoryPort = Depends(get_user_repository),
    email_service: EmailServicePort = Depends(get_email_service),
    audit_service: AuditServicePort = Depends(get_audit_service)
) -> DeactivateUserCommand:
    """Dependency para obtener comando de desactivar usuario"""
    return DeactivateUserCommand(user_repository, email_service, audit_service)


# Queries (casos de uso de lectura)
async def get_user_query(
    user_repository: UserRepositoryPort = Depends(get_user_repository)
) -> GetUserQuery:
    """Dependency para obtener query de usuario"""
    return GetUserQuery(user_repository)


async def get_user_by_email_query(
    user_repository: UserRepositoryPort = Depends(get_user_repository)
) -> GetUserByEmailQuery:
    """Dependency para obtener query de usuario por email"""
    return GetUserByEmailQuery(user_repository)


async def get_list_users_query(
    user_repository: UserRepositoryPort = Depends(get_user_repository)
) -> ListUsersQuery:
    """Dependency para obtener query de lista de usuarios"""
    return ListUsersQuery(user_repository)


async def get_search_users_query(
    user_repository: UserRepositoryPort = Depends(get_user_repository)
) -> SearchUsersQuery:
    """Dependency para obtener query de búsqueda de usuarios"""
    return SearchUsersQuery(user_repository)


# Repositorios para Beneficios
async def get_beneficio_repository(
    session: AsyncSession = Depends(get_db)
) -> BeneficioRepositoryPort:
    """Dependency para obtener repositorio de beneficios"""
    return BeneficioRepository(session)


# Comandos para Beneficios
async def get_create_beneficio_command(
    beneficio_repository: BeneficioRepositoryPort = Depends(get_beneficio_repository)
) -> CreateBeneficioCommand:
    """Dependency para obtener comando de crear beneficio"""
    return CreateBeneficioCommand(beneficio_repository)


async def get_update_beneficio_command(
    beneficio_repository: BeneficioRepositoryPort = Depends(get_beneficio_repository)
) -> UpdateBeneficioCommand:
    """Dependency para obtener comando de actualizar beneficio"""
    return UpdateBeneficioCommand(beneficio_repository)


async def get_deactivate_beneficio_command(
    beneficio_repository: BeneficioRepositoryPort = Depends(get_beneficio_repository)
) -> DeactivateBeneficioCommand:
    """Dependency para obtener comando de desactivar beneficio"""
    return DeactivateBeneficioCommand(beneficio_repository)


# Queries para Beneficios
async def get_beneficio_query(
    beneficio_repository: BeneficioRepositoryPort = Depends(get_beneficio_repository)
) -> GetBeneficioQuery:
    """Dependency para obtener query de beneficio"""
    return GetBeneficioQuery(beneficio_repository)


async def get_list_beneficios_query(
    beneficio_repository: BeneficioRepositoryPort = Depends(get_beneficio_repository)
) -> ListBeneficiosQuery:
    """Dependency para obtener query de lista de beneficios"""
    return ListBeneficiosQuery(beneficio_repository)


async def get_search_beneficios_query(
    beneficio_repository: BeneficioRepositoryPort = Depends(get_beneficio_repository)
) -> SearchBeneficiosQuery:
    """Dependency para obtener query de búsqueda de beneficios"""
    return SearchBeneficiosQuery(beneficio_repository)
