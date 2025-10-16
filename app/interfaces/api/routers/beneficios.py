"""Router para endpoints de beneficios"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form

from app.application.beneficios import (
    CreateBeneficioCommand,
    UpdateBeneficioCommand,
    DeactivateBeneficioCommand,
    GetBeneficioQuery,
    ListBeneficiosQuery,
    SearchBeneficiosQuery,
    CreateBeneficioDTO,
    UpdateBeneficioDTO,
    BeneficioFilterDTO
)
from app.core.exceptions import BaseAppException
from app.core.security import CurrentUser
from app.core.utils.file_utils import file_manager
from app.infrastructure.auth import get_current_user, require_admin, require_manager_or_admin
from app.interfaces.api.dependencies import (
    get_create_beneficio_command,
    get_update_beneficio_command,
    get_deactivate_beneficio_command,
    get_beneficio_query,
    get_list_beneficios_query,
    get_search_beneficios_query
)
from app.interfaces.api.schemas import (
    BeneficioCreateRequest,
    BeneficioUpdateRequest,
    BeneficioResponse,
    BeneficioListResponse,
    BeneficioSummaryResponse,
    ErrorResponse
)
from app.domain.beneficios.services.beneficio_service import BeneficioService

router = APIRouter(prefix="/beneficios", tags=["beneficios"])


@router.post(
    "/",
    response_model=BeneficioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear beneficio",
    description="Crea un nuevo beneficio en el sistema con imagen. Requiere permisos de administrador.",
    responses={
        201: {"description": "Beneficio creado exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos inválidos o archivo no válido"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        409: {"model": ErrorResponse, "description": "Beneficio ya existe"}
    }
)
async def create_beneficio(
    imagen: UploadFile = File(..., description="Archivo de imagen del beneficio"),
    beneficio: str = Form(..., description="Nombre del beneficio"),
    detalle: str = Form(..., description="Descripción detallada del beneficio"),
    regla1: str = Form(..., description="Primera regla del beneficio"),
    regla2: str = Form(..., description="Segunda regla del beneficio"),
    valor: int = Form(..., ge=0, description="Valor en puntos del beneficio"),
    current_user: CurrentUser = Depends(require_admin),
    command: CreateBeneficioCommand = Depends(get_create_beneficio_command)
) -> BeneficioResponse:
    """Crea un nuevo beneficio con imagen"""
    try:
        # Guardar la imagen y obtener la URL
        image_url = await file_manager.save_beneficio_image(imagen)
        
        # Crear DTO con la URL de la imagen
        dto = CreateBeneficioDTO(
            beneficio=beneficio,
            detalle=detalle,
            regla1=regla1,
            regla2=regla2,
            valor=valor,
            imagen=image_url
        )
        
        result = await command.execute(dto, current_user)
        
        return BeneficioResponse(
            id=result.id,
            imagen=result.imagen,
            beneficio=result.beneficio,
            detalle=result.detalle,
            regla1=result.regla1,
            regla2=result.regla2,
            valor=result.valor,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
        
    except BaseAppException as e:
        if "ya existe" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": e.message, "error_code": e.error_code, "details": e.details}
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )
    except Exception as e:
        # Si hay error después de guardar la imagen, intentar limpiarla
        if 'image_url' in locals():
            file_manager.delete_beneficio_image(image_url)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Error interno del servidor", "error_code": "BENEFICIO-ERR-500"}
        )


@router.get(
    "/{beneficio_id}",
    response_model=BeneficioResponse,
    summary="Obtener beneficio por ID",
    description="Obtiene un beneficio específico por su ID",
    responses={
        200: {"description": "Beneficio encontrado"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        404: {"model": ErrorResponse, "description": "Beneficio no encontrado"}
    }
)
async def get_beneficio(
    beneficio_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    query: GetBeneficioQuery = Depends(get_beneficio_query)
) -> BeneficioResponse:
    """Obtiene un beneficio por ID"""
    try:
        result = await query.execute(beneficio_id)
        
        return BeneficioResponse(
            id=result.id,
            imagen=result.imagen,
            beneficio=result.beneficio,
            detalle=result.detalle,
            regla1=result.regla1,
            regla2=result.regla2,
            valor=result.valor,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at
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
    "/{beneficio_id}",
    response_model=BeneficioResponse,
    summary="Actualizar beneficio",
    description="Actualiza la información de un beneficio. Requiere permisos de manager o admin.",
    responses={
        200: {"description": "Beneficio actualizado exitosamente"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        404: {"model": ErrorResponse, "description": "Beneficio no encontrado"}
    }
)
async def update_beneficio(
    beneficio_id: UUID,
    request: BeneficioUpdateRequest,
    current_user: CurrentUser = Depends(require_manager_or_admin),
    command: UpdateBeneficioCommand = Depends(get_update_beneficio_command)
) -> BeneficioResponse:
    """Actualiza un beneficio"""
    try:
        dto = UpdateBeneficioDTO(
            imagen=request.imagen,
            beneficio=request.beneficio,
            detalle=request.detalle,
            regla1=request.regla1,
            regla2=request.regla2,
            valor=request.valor
        )
        
        result = await command.execute(beneficio_id, dto, current_user)
        
        return BeneficioResponse(
            id=result.id,
            imagen=result.imagen,
            beneficio=result.beneficio,
            detalle=result.detalle,
            regla1=result.regla1,
            regla2=result.regla2,
            valor=result.valor,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at
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
    response_model=BeneficioListResponse,
    summary="Listar beneficios",
    description="Lista beneficios con filtros y paginación",
    responses={
        200: {"description": "Lista de beneficios"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def list_beneficios(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_user: CurrentUser = Depends(get_current_user),
    query: ListBeneficiosQuery = Depends(get_list_beneficios_query)
) -> BeneficioListResponse:
    """Lista beneficios con filtros y paginación"""
    try:
        filters = BeneficioFilterDTO(
            page=page,
            size=size,
            is_active=is_active
        )
        
        result = await query.execute(filters)
        
        return BeneficioListResponse(
            beneficios=[
                BeneficioResponse(
                    id=beneficio.id,
                    imagen=beneficio.imagen,
                    beneficio=beneficio.beneficio,
                    detalle=beneficio.detalle,
                    regla1=beneficio.regla1,
                    regla2=beneficio.regla2,
                    valor=beneficio.valor,
                    is_active=beneficio.is_active,
                    created_at=beneficio.created_at,
                    updated_at=beneficio.updated_at
                ) for beneficio in result.beneficios
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


@router.delete(
    "/{beneficio_id}",
    response_model=BeneficioResponse,
    summary="Desactivar beneficio",
    description="Desactiva un beneficio (soft delete). Requiere permisos de administrador.",
    responses={
        200: {"description": "Beneficio desactivado exitosamente"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        404: {"model": ErrorResponse, "description": "Beneficio no encontrado"}
    }
)
async def deactivate_beneficio(
    beneficio_id: UUID,
    current_user: CurrentUser = Depends(require_admin),
    command: DeactivateBeneficioCommand = Depends(get_deactivate_beneficio_command)
) -> BeneficioResponse:
    """Desactiva un beneficio"""
    try:
        result = await command.execute(beneficio_id, current_user)
        
        return BeneficioResponse(
            id=result.id,
            imagen=result.imagen,
            beneficio=result.beneficio,
            detalle=result.detalle,
            regla1=result.regla1,
            regla2=result.regla2,
            valor=result.valor,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at
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
    response_model=BeneficioListResponse,
    summary="Buscar beneficios",
    description="Busca beneficios por texto en nombre, detalle o reglas",
    responses={
        200: {"description": "Resultados de búsqueda"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def search_beneficios(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    current_user: CurrentUser = Depends(get_current_user),
    query: SearchBeneficiosQuery = Depends(get_search_beneficios_query)
) -> BeneficioListResponse:
    """Busca beneficios por texto"""
    try:
        result = await query.execute(q, page, size)
        
        return BeneficioListResponse(
            beneficios=[
                BeneficioResponse(
                    id=beneficio.id,
                    imagen=beneficio.imagen,
                    beneficio=beneficio.beneficio,
                    detalle=beneficio.detalle,
                    regla1=beneficio.regla1,
                    regla2=beneficio.regla2,
                    valor=beneficio.valor,
                    is_active=beneficio.is_active,
                    created_at=beneficio.created_at,
                    updated_at=beneficio.updated_at
                ) for beneficio in result.beneficios
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


@router.get(
    "/summary/",
    response_model=BeneficioSummaryResponse,
    summary="Resumen de beneficios",
    description="Obtiene estadísticas generales de los beneficios",
    responses={
        200: {"description": "Resumen de beneficios"},
        401: {"model": ErrorResponse, "description": "No autenticado"}
    }
)
async def get_beneficios_summary(
    current_user: CurrentUser = Depends(get_current_user),
    query: ListBeneficiosQuery = Depends(get_list_beneficios_query)
) -> BeneficioSummaryResponse:
    """Obtiene resumen de beneficios"""
    try:
        # Obtener todos los beneficios
        all_filters = BeneficioFilterDTO(page=1, size=1000)  # Obtener todos
        all_result = await query.execute(all_filters)
        
        # Obtener solo activos
        active_filters = BeneficioFilterDTO(page=1, size=1000, is_active=True)
        active_result = await query.execute(active_filters)
        
        # Calcular valor total de beneficios activos
        valor_total = BeneficioService.calculate_total_value(active_result.beneficios)
        
        return BeneficioSummaryResponse(
            total_beneficios=all_result.total,
            beneficios_activos=active_result.total,
            valor_total=valor_total
        )
        
    except BaseAppException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )


@router.put(
    "/{beneficio_id}/imagen",
    response_model=BeneficioResponse,
    summary="Actualizar imagen de beneficio",
    description="Actualiza solo la imagen de un beneficio. Requiere permisos de manager o admin.",
    responses={
        200: {"description": "Imagen actualizada exitosamente"},
        400: {"model": ErrorResponse, "description": "Archivo no válido"},
        401: {"model": ErrorResponse, "description": "No autenticado"},
        403: {"model": ErrorResponse, "description": "Sin permisos"},
        404: {"model": ErrorResponse, "description": "Beneficio no encontrado"}
    }
)
async def update_beneficio_image(
    beneficio_id: UUID,
    imagen: UploadFile = File(..., description="Nueva imagen del beneficio"),
    current_user: CurrentUser = Depends(require_manager_or_admin),
    command: UpdateBeneficioCommand = Depends(get_update_beneficio_command),
    query: GetBeneficioQuery = Depends(get_beneficio_query)
) -> BeneficioResponse:
    """Actualiza la imagen de un beneficio"""
    try:
        # Obtener beneficio actual para eliminar imagen anterior
        current_beneficio = await query.execute(beneficio_id)
        
        # Guardar nueva imagen
        new_image_url = await file_manager.save_beneficio_image(imagen)
        
        # Actualizar beneficio con nueva imagen
        dto = UpdateBeneficioDTO(imagen=new_image_url)
        result = await command.execute(beneficio_id, dto, current_user)
        
        # Eliminar imagen anterior si existía
        if current_beneficio.imagen:
            file_manager.delete_beneficio_image(current_beneficio.imagen)
        
        return BeneficioResponse(
            id=result.id,
            imagen=result.imagen,
            beneficio=result.beneficio,
            detalle=result.detalle,
            regla1=result.regla1,
            regla2=result.regla2,
            valor=result.valor,
            is_active=result.is_active,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
        
    except BaseAppException as e:
        if "no encontrado" in e.message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": e.message, "error_code": e.error_code, "details": e.details}
            )
        # Si hay error después de guardar la nueva imagen, limpiarla
        if 'new_image_url' in locals():
            file_manager.delete_beneficio_image(new_image_url)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code, "details": e.details}
        )
