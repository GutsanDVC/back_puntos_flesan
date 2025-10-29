"""Router de beneficios - Endpoints REST"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.beneficio_schema import (
    BeneficioResponse,
    BeneficioListResponse,
    BeneficioSummaryResponse
)
from app.core.database import get_db
from app.core.exceptions import BaseAppException, NotFoundError, ConflictError, ValidationError
from app.core.security import CurrentUser
from app.core.utils.file_utils import file_manager
from app.core.auth import get_current_user, require_admin, require_manage_benefits
from app.repositories.beneficio_repository import BeneficioRepository
from app.services.beneficio_service import BeneficioService


router = APIRouter(prefix="/beneficios", tags=["beneficios"])


def get_beneficio_service(db: AsyncSession = Depends(get_db)) -> BeneficioService:
    """Dependencia para obtener el servicio de beneficios"""
    repository = BeneficioRepository(db)
    return BeneficioService(repository)

#current_user: CurrentUser = Depends(require_manage_benefits),
@router.post(
    "/",
    response_model=BeneficioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear beneficio",
    description="Crea un nuevo beneficio con imagen. Requiere permisos de administrador."
)
async def create_beneficio(
    imagen: UploadFile = File(..., description="Archivo de imagen del beneficio"),
    beneficio: str = Form(..., description="Nombre del beneficio"),
    detalle: str = Form(..., description="Descripción detallada"),
    valor: int = Form(..., ge=0, description="Valor en puntos"),
    
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioResponse:
    """Crea un nuevo beneficio con imagen"""
    try:
        # Guardar la imagen y obtener la URL
        image_url = await file_manager.save_beneficio_image(imagen)
        
        # Crear beneficio
        result = await service.create_beneficio(
            beneficio=beneficio,
            detalle=detalle,
            valor=valor,
            imagen=image_url
        )
        
        return BeneficioResponse(**result)
        
    except ConflictError as e:
        # Si hay error, eliminar imagen guardada
        if 'image_url' in locals():
            await file_manager.delete_beneficio_image(image_url)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except ValidationError as e:
        # Si hay error, eliminar imagen guardada
        if 'image_url' in locals():
            await file_manager.delete_beneficio_image(image_url)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except Exception as e:
        # Si hay error, eliminar imagen guardada
        if 'image_url' in locals():
            await file_manager.delete_beneficio_image(image_url)
        raise


@router.get(
    "/{beneficio_id}",
    response_model=BeneficioResponse,
    summary="Obtener beneficio por ID"
)
async def get_beneficio(
    beneficio_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioResponse:
    """Obtiene un beneficio por ID"""
    try:
        result = await service.get_beneficio_by_id(beneficio_id)
        return BeneficioResponse(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.put(
    "/{beneficio_id}",
    response_model=BeneficioResponse,
    summary="Actualizar beneficio",
    description="Actualiza un beneficio. Requiere permisos de administrador."
)
async def update_beneficio(
    beneficio_id: UUID,
    imagen: Optional[str] = Form(None),
    beneficio: Optional[str] = Form(None),
    detalle: Optional[str] = Form(None),
    valor: Optional[int] = Form(None, ge=0),
    current_user: CurrentUser = Depends(require_manage_benefits),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioResponse:
    """Actualiza un beneficio"""
    try:
        result = await service.update_beneficio(
            beneficio_id=beneficio_id,
            imagen=imagen,
            beneficio=beneficio,
            detalle=detalle,
            valor=valor
        )
        
        return BeneficioResponse(**result)
        
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


@router.put(
    "/{beneficio_id}/imagen",
    response_model=BeneficioResponse,
    summary="Actualizar solo imagen del beneficio"
)
async def update_beneficio_imagen(
    beneficio_id: UUID,
    imagen: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_manage_benefits),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioResponse:
    """Actualiza solo la imagen de un beneficio"""
    try:
        # Obtener beneficio actual para eliminar imagen anterior
        current_beneficio = await service.get_beneficio_by_id(beneficio_id)
        old_image_url = current_beneficio["imagen"]
        
        # Guardar nueva imagen
        new_image_url = await file_manager.save_beneficio_image(imagen)
        
        # Actualizar beneficio
        result = await service.update_beneficio(
            beneficio_id=beneficio_id,
            imagen=new_image_url
        )
        
        # Eliminar imagen anterior
        if old_image_url:
            await file_manager.delete_beneficio_image(old_image_url)
        
        return BeneficioResponse(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )
    except Exception as e:
        # Si hay error, eliminar nueva imagen
        if 'new_image_url' in locals():
            await file_manager.delete_beneficio_image(new_image_url)
        raise


@router.put(
    "/{beneficio_id}/desactivar",
    response_model=BeneficioResponse,
    summary="Desactivar beneficio",
    description="Desactiva un beneficio (soft delete). Requiere permisos de administrador."
)
async def deactivate_beneficio(
    beneficio_id: UUID,
    current_user: CurrentUser = Depends(require_manage_benefits),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioResponse:
    """Desactiva un beneficio"""
    try:
        result = await service.deactivate_beneficio(beneficio_id)
        return BeneficioResponse(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.put(
    "/{beneficio_id}/activar",
    response_model=BeneficioResponse,
    summary="Activar beneficio",
    description="Activa un beneficio. Requiere permisos de administrador."
)
async def activate_beneficio(
    beneficio_id: UUID,
    current_user: CurrentUser = Depends(require_manage_benefits),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioResponse:
    """Activa un beneficio"""
    try:
        result = await service.activate_beneficio(beneficio_id)
        return BeneficioResponse(**result)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.get(
    "/",
    response_model=BeneficioListResponse,
    summary="Listar beneficios",
    description="Lista beneficios con paginación y filtros"
)
async def list_beneficios(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioListResponse:
    """Lista beneficios con paginación y filtros"""
    try:
        result = await service.list_beneficios(
            page=page,
            size=size,
            is_active=is_active
        )
        
        return BeneficioListResponse(
            beneficios=[BeneficioResponse(**b) for b in result["beneficios"]],
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
    response_model=BeneficioListResponse,
    summary="Buscar beneficios",
    description="Busca beneficios por texto en nombre, detalle o reglas"
)
async def search_beneficios(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioListResponse:
    """Busca beneficios por texto"""
    try:
        result = await service.search_beneficios(
            query=q,
            page=page,
            size=size
        )
        
        return BeneficioListResponse(
            beneficios=[BeneficioResponse(**b) for b in result["beneficios"]],
            total=result["total"],
            page=result["page"],
            size=result["size"],
            total_pages=result["total_pages"]
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code}
        )


@router.get(
    "/summary/",
    response_model=BeneficioSummaryResponse,
    summary="Resumen de beneficios",
    description="Obtiene estadísticas de beneficios"
)
async def get_summary(
    current_user: CurrentUser = Depends(get_current_user),
    service: BeneficioService = Depends(get_beneficio_service)
) -> BeneficioSummaryResponse:
    """Obtiene resumen estadístico de beneficios"""
    result = await service.get_summary()
    return BeneficioSummaryResponse(**result)
