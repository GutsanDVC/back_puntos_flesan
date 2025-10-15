"""Router para endpoints de usuarios"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.users import (
    CreateUserCommand,
    UpdateUserCommand,
    AssignRoleCommand,
    DeactivateUserCommand,
    GetUserQuery,
    ListUsersQuery,
    SearchUsersQuery,
    CreateUserDTO,
    UpdateUserDTO,
    AssignRoleDTO,
    UserFilterDTO
)
from app.core.exceptions import BaseAppException
from app.core.security import CurrentUser
from app.infrastructure.auth import get_current_user, require_admin, require_manager_or_admin
from app.interfaces.api.dependencies import (
    get_create_user_command,
    get_update_user_command,
    get_assign_role_command,
    get_deactivate_user_command,
    get_user_query,
    get_list_users_query,
    get_search_users_query
)
from app.interfaces.api.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    AssignRoleRequest,
    UserResponse,
    UserListResponse,
    ErrorResponse
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema. Requiere permisos de administrador.",
    responses={
        201: {"description": "Usuario creado exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        409: {"model": ErrorResponse, "description": "Email ya existe"}
    }
)
async def create_user(
    request: UserCreateRequest,
    current_user: CurrentUser = Depends(require_admin),
    command: CreateUserCommand = Depends(get_create_user_command)
) -> UserResponse:
    """Crea un nuevo usuario"""
    try:
        dto = CreateUserDTO(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            roles=request.roles
        )
        
        result = await command.execute(dto, current_user)
        
        return UserResponse(
            id=result.id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            full_name=result.full_name,
            roles=result.roles,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at,
            last_login=result.last_login
        )
        
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por ID",
    description="Obtiene un usuario específico por su ID",
    responses={
        200: {"description": "Usuario encontrado"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"}
    }
)
async def get_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    query: GetUserQuery = Depends(get_user_query)
) -> UserResponse:
    """Obtiene un usuario por ID"""
    try:
        result = await query.execute(user_id)
        
        return UserResponse(
            id=result.id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            full_name=result.full_name,
            roles=result.roles,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at,
            last_login=result.last_login
        )
        
    except BaseAppException as e:
        if "no encontrado" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "error_code": e.error_code, "details": e.details}
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario",
    description="Actualiza la información de un usuario. Requiere permisos de manager o admin.",
    responses={
        200: {"description": "Usuario actualizado exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"}
    }
)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    current_user: CurrentUser = Depends(require_manager_or_admin),
    command: UpdateUserCommand = Depends(get_update_user_command)
) -> UserResponse:
    """Actualiza un usuario"""
    try:
        dto = UpdateUserDTO(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email
        )
        
        result = await command.execute(user_id, dto, current_user)
        
        return UserResponse(
            id=result.id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            full_name=result.full_name,
            roles=result.roles,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at,
            last_login=result.last_login
        )
        
    except BaseAppException as e:
        if "no encontrado" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "error_code": e.error_code, "details": e.details}
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Lista usuarios con filtros y paginación",
    responses={
        200: {"description": "Lista de usuarios"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def list_users(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_user: CurrentUser = Depends(get_current_user),
    query: ListUsersQuery = Depends(get_list_users_query)
) -> UserListResponse:
    """Lista usuarios con filtros y paginación"""
    try:
        filters = UserFilterDTO(
            page=page,
            size=size,
            email=email,
            is_active=is_active
        )
        
        result = await query.execute(filters)
        
        return UserListResponse(
            users=[
                UserResponse(
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
                ) for user in result.users
            ],
            total=result.total,
            page=result.page,
            size=result.size,
            total_pages=result.total_pages
        )
        
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.post(
    "/{user_id}/roles",
    response_model=UserResponse,
    summary="Asignar rol a usuario",
    description="Asigna un rol a un usuario. Requiere permisos de administrador.",
    responses={
        200: {"description": "Rol asignado exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"}
    }
)
async def assign_role(
    user_id: UUID,
    request: AssignRoleRequest,
    current_user: CurrentUser = Depends(require_admin),
    command: AssignRoleCommand = Depends(get_assign_role_command)
) -> UserResponse:
    """Asigna un rol a un usuario"""
    try:
        dto = AssignRoleDTO(
            user_id=user_id,
            role=request.role
        )
        
        result = await command.execute(dto, current_user)
        
        return UserResponse(
            id=result.id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            full_name=result.full_name,
            roles=result.roles,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at,
            last_login=result.last_login
        )
        
    except BaseAppException as e:
        if "no encontrado" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "error_code": e.error_code, "details": e.details}
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Desactivar usuario",
    description="Desactiva un usuario (soft delete). Requiere permisos de administrador.",
    responses={
        200: {"description": "Usuario desactivado exitosamente"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        404: {"model": ErrorResponse, "description": "Usuario no encontrado"}
    }
)
async def deactivate_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(require_admin),
    command: DeactivateUserCommand = Depends(get_deactivate_user_command)
) -> UserResponse:
    """Desactiva un usuario"""
    try:
        result = await command.execute(user_id, current_user)
        
        return UserResponse(
            id=result.id,
            email=result.email,
            first_name=result.first_name,
            last_name=result.last_name,
            full_name=result.full_name,
            roles=result.roles,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at,
            last_login=result.last_login
        )
        
    except BaseAppException as e:
        if "no encontrado" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "error_code": e.error_code, "details": e.details}
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.get(
    "/search/",
    response_model=UserListResponse,
    summary="Buscar usuarios",
    description="Busca usuarios por texto en nombre, apellido o email",
    responses={
        200: {"description": "Resultados de búsqueda"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def search_users(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    current_user: CurrentUser = Depends(get_current_user),
    query: SearchUsersQuery = Depends(get_search_users_query)
) -> UserListResponse:
    """Busca usuarios por texto"""
    try:
        result = await query.execute(q, page, size)
        
        return UserListResponse(
            users=[
                UserResponse(
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
                ) for user in result.users
            ],
            total=result.total,
            page=result.page,
            size=result.size,
            total_pages=result.total_pages
        )
        
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )
