"""Router de canjes - Endpoints REST para canje de puntos"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.canje_schema import (
    CanjeCreateRequest,
    CanjeResponse,
    CanjeListResponse,
    CanjeEstadoUpdate
)
from app.core.database import get_db
from app.core.exceptions import BaseAppException, NotFoundError, ValidationError
from app.core.auth import get_current_user
from app.core.security import CurrentUser
from app.repositories.canje_repository import CanjeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.beneficio_repository import BeneficioRepository
from app.services.canje_service import CanjeService


router = APIRouter(prefix="/canjes", tags=["canjes"])


def get_canje_service(db: AsyncSession = Depends(get_db)) -> CanjeService:
    """Dependencia para obtener el servicio de canjes"""
    canje_repository = CanjeRepository(db)
    user_repository = UserRepository(db)
    beneficio_repository = BeneficioRepository(db)
    return CanjeService(canje_repository, user_repository, beneficio_repository)


@router.post(
    "/",
    response_model=CanjeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Canjear puntos por beneficio",
    description="""
    Crea un nuevo canje de puntos por un beneficio.
    
    **Validaciones:**
    - Usuario existe y está activo
    - Beneficio existe y está activo
    - Usuario tiene puntos suficientes
    - Puntos a utilizar <= puntos disponibles del usuario
    - Fecha de uso > fecha de canje
    - Usuario no tiene más de 30 días de vacaciones acumulados
    
    **Efecto:**
    - Se registra el canje en el historial
    - Se descuentan los puntos del usuario automáticamente
    """
)
async def crear_canje(
    request: CanjeCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: CanjeService = Depends(get_canje_service)
) -> CanjeResponse:
    """
    Crea un nuevo canje de puntos por beneficio
    
    Este endpoint valida todas las reglas de negocio y realiza el descuento
    automático de puntos al usuario
    """
    try:
        print(request)
        canje = await service.crear_canje(
            user_id=request.user_id,
            beneficio_id=request.beneficio_id,
            puntos_utilizar=request.puntos_utilizar,
            fecha_canje=request.fecha_canje,
            fecha_uso=request.fecha_uso,
            observaciones=request.observaciones
        )
        return CanjeResponse(**canje)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
    "/{canje_id}",
    response_model=CanjeResponse,
    summary="Obtener canje por ID",
    description="Obtiene la información detallada de un canje específico"
)
async def get_canje(
    canje_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: CanjeService = Depends(get_canje_service)
) -> CanjeResponse:
    """Obtiene un canje por ID"""
    try:
        canje = await service.get_canje_by_id(canje_id)
        return CanjeResponse(**canje)
        
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
    "/usuario/{user_id}",
    response_model=CanjeListResponse,
    summary="Listar canjes de un usuario",
    description="Obtiene todos los canjes realizados por un usuario específico con paginación"
)
async def get_canjes_usuario(
    user_id: int,
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (ACTIVO, USADO, CANCELADO, VENCIDO)"),
    current_user: CurrentUser = Depends(get_current_user),
    service: CanjeService = Depends(get_canje_service)
) -> CanjeListResponse:
    """Lista los canjes de un usuario con paginación y filtros"""
    try:
        result = await service.get_canjes_by_user(
            user_id=user_id,
            page=page,
            size=size,
            estado=estado
        )
        
        return CanjeListResponse(
            canjes=[CanjeResponse(**canje) for canje in result["canjes"]],
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
    "/",
    response_model=CanjeListResponse,
    summary="Listar todos los canjes",
    description="Lista todos los canjes con paginación y filtros. Requiere autenticación."
)
async def list_canjes(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    user_id: Optional[int] = Query(None, description="Filtrar por user_id"),
    beneficio_id: Optional[int] = Query(None, description="Filtrar por beneficio_id"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    current_user: CurrentUser = Depends(get_current_user),
    service: CanjeService = Depends(get_canje_service)
) -> CanjeListResponse:
    """Lista todos los canjes con paginación y filtros"""
    try:
        result = await service.list_canjes(
            page=page,
            size=size,
            user_id=user_id,
            beneficio_id=beneficio_id,
            estado=estado
        )
        
        return CanjeListResponse(
            canjes=[CanjeResponse(**canje) for canje in result["canjes"]],
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


@router.patch(
    "/{canje_id}/estado",
    response_model=CanjeResponse,
    summary="Actualizar estado de canje",
    description="""
    Actualiza el estado de un canje existente.
    
    **Estados permitidos:**
    - ACTIVO: Canje vigente sin usar
    - USADO: Beneficio ya utilizado
    - CANCELADO: Canje cancelado (devuelve puntos al usuario)
    - VENCIDO: Canje vencido sin uso
    
    **Nota:** Si se cancela un canje ACTIVO, los puntos se devuelven automáticamente al usuario.
    """
)
async def actualizar_estado_canje(
    canje_id: UUID,
    request: CanjeEstadoUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: CanjeService = Depends(get_canje_service)
) -> CanjeResponse:
    """Actualiza el estado de un canje"""
    try:
        canje = await service.actualizar_estado_canje(
            canje_id=canje_id,
            estado=request.estado,
            observaciones=request.observaciones
        )
        return CanjeResponse(**canje)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
