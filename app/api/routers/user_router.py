"""Router de usuarios - Endpoints REST"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse
)
from app.core.database import get_db
from app.core.exceptions import BaseAppException, NotFoundError, ConflictError, ValidationError
from app.core.security import CurrentUser
from app.core.auth import get_current_user, require_admin
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependencia para obtener el servicio de usuarios"""
    repository = UserRepository(db)
    return UserService(repository)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario. Requiere permisos de administrador."
)
async def create_user(
    request: UserCreateRequest,
    current_user: CurrentUser = Depends(require_admin),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Crea un nuevo usuario"""
    try:
        user = await service.create_user(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            roles=request.roles
        )
        return UserResponse(**user)
        
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por user_id"
)
async def get_user(
    user_id:int,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Obtiene un usuario por ID interno (UUID)"""
    try:
        user = await service.get_user_by_id(user_id)
        return UserResponse(**user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.get(
    "/by-user-id/{user_id}",
    response_model=UserResponse,
    summary="Obtener usuario por user_id (datawarehouse)",
    description="Obtiene un usuario por su user_id del datawarehouse (ID externo tipo INTEGER)"
)
async def get_user_by_user_id(
    user_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Obtiene un usuario por user_id del datawarehouse"""
    try:
        user = await service.get_user_by_user_id(user_id)
        return UserResponse(**user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario"
)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Actualiza un usuario"""
    try:
        user = await service.update_user(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email
        )
        return UserResponse(**user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Desactivar usuario",
    description="Desactiva un usuario (soft delete). Requiere permisos de administrador."
)
async def deactivate_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(require_admin),
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Desactiva un usuario"""
    try:
        user = await service.deactivate_user(user_id)
        return UserResponse(**user)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Lista usuarios con paginación y filtros"
)
async def list_users(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    email: Optional[str] = Query(None, description="Filtrar por email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserListResponse:
    """Lista usuarios con paginación y filtros"""
    try:
        result = await service.list_users(
            page=page,
            size=size,
            email=email,
            is_active=is_active
        )
        
        return UserListResponse(
            users=[UserResponse(**user) for user in result["users"]],
            total=result["total"],
            page=result["page"],
            size=result["size"],
            total_pages=result["total_pages"]
        )
        
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.get(
    "/search/",
    response_model=UserListResponse,
    summary="Buscar usuarios",
    description="Busca usuarios por email"
)
async def search_users(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
) -> UserListResponse:
    """Busca usuarios por email"""
    try:
        logger.debug(
            {"Query": q,
            "Page": page,
            "Current User": current_user,
            "request": request,
            "Size": size}
        )
        result = await service.search_users(
            query=q,
            page=page,
            size=size
        )
        
        return UserListResponse(
            users=[UserResponse(**user) for user in result["users"]],
            total=result["total"],
            page=result["page"],
            size=result["size"],
            total_pages=result["total_pages"]
        )
        
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
