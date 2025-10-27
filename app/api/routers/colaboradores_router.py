"""Router de consultas de colaboradores desde el datawarehouse"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query

from app.application.datawarehouse.services.colaboradores_service import colaboradores_service
from app.application.datawarehouse.dto.colaboradores_dto import (
    ColaboradorQueryDTO,
    ColaboradorSearchDTO,
    ColaboradoresListResponseDTO,
    ColaboradorInfoDTO
)
from app.core.security import CurrentUser
from app.infrastructure.auth import require_admin
from app.infrastructure.datawarehouse.exceptions import DatawarehouseException


router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])


@router.get("/", response_model=ColaboradoresListResponseDTO, summary="Listar colaboradores")
async def get_colaboradores(
    empl_status: Optional[str] = Query(None, description="Estado del empleado"),
    user_id: Optional[int] = Query(None, description="ID del usuario"),
    national_id: Optional[str] = Query(None, description="Cédula nacional"),
    first_name: Optional[str] = Query(None, description="Primer nombre"),
    last_name: Optional[str] = Query(None, description="Apellido paterno"),
    correo_flesan: Optional[str] = Query(None, description="Correo corporativo"),
    centro_costo: Optional[str] = Query(None, description="Centro de costo"),
    external_cod_cargo: Optional[str] = Query(None, description="Código externo del cargo"),
    external_cod_tipo_contrato: Optional[str] = Query(None, description="Código tipo de contrato"),
    np_lider: Optional[str] = Query(None, description="Nombre del líder"),
    order_by: Optional[str] = Query(None, description="Campo para ordenar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: CurrentUser = Depends(require_admin)
):
    """Lista colaboradores con filtros opcionales. Requiere rol ADMIN"""
    try:
        filter_params = {
            "empl_status": empl_status,
            "user_id": user_id,
            "national_id": national_id,
            "first_name": first_name,
            "last_name": last_name,
            "correo_flesan": correo_flesan,
            "centro_costo": centro_costo,
            "external_cod_cargo": external_cod_cargo,
            "external_cod_tipo_contrato": external_cod_tipo_contrato,
            "np_lider": np_lider
        }
        
        filters = {k: v for k, v in filter_params.items() if v is not None}
        
        result = await colaboradores_service.get_colaboradores(
            filters=filters if filters else None,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        
        return ColaboradoresListResponseDTO(
            data=result,
            total_records=len(result),
            limit=limit,
            offset=offset,
            filters_applied=filters if filters else None
        )
        
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/query", response_model=ColaboradoresListResponseDTO, summary="Consulta avanzada")
async def query_colaboradores(
    query_data: ColaboradorQueryDTO,
    current_user: CurrentUser = Depends(require_admin)
):
    """Consulta colaboradores con filtros avanzados (POST). Requiere rol ADMIN"""
    try:
        filters = None
        if query_data.filters:
            filters = query_data.filters.to_dict()
        
        result = await colaboradores_service.get_colaboradores(
            filters=filters,
            columns=query_data.columns,
            order_by=query_data.order_by,
            limit=query_data.limit,
            offset=query_data.offset
        )
        
        return ColaboradoresListResponseDTO(
            data=result,
            total_records=len(result),
            limit=query_data.limit,
            offset=query_data.offset,
            filters_applied=filters
        )
        
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/user/{user_id}", summary="Obtener por user_id")
async def get_colaborador_by_user_id(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin)
):
    """Obtiene un colaborador específico por user_id. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.get_colaborador_by_user_id(user_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Colaborador con user_id {user_id} no encontrado")
        return result
        
    except HTTPException:
        raise
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/national-id/{national_id}", summary="Obtener por cédula")
async def get_colaborador_by_national_id(
    national_id: str,
    current_user: CurrentUser = Depends(require_admin)
):
    """Obtiene un colaborador específico por cédula nacional. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.get_colaborador_by_national_id(national_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Colaborador con cédula {national_id} no encontrado")
        return result
        
    except HTTPException:
        raise
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/activos", response_model=ColaboradoresListResponseDTO, summary="Colaboradores activos")
async def get_colaboradores_activos(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_admin)
):
    """Lista colaboradores con estado activo. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.get_colaboradores_activos(
            limit=limit,
            offset=offset
        )
        return ColaboradoresListResponseDTO(
            data=result,
            total_records=len(result),
            limit=limit,
            offset=offset,
            filters_applied={"empl_status": "A"}
        )
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/centro-costo/{centro_costo}", response_model=ColaboradoresListResponseDTO, summary="Por centro de costo")
async def get_colaboradores_by_centro_costo(
    centro_costo: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_admin)
):
    """Lista colaboradores por centro de costo. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.get_colaboradores_by_centro_costo(
            centro_costo=centro_costo,
            limit=limit,
            offset=offset
        )
        return ColaboradoresListResponseDTO(
            data=result,
            total_records=len(result),
            limit=limit,
            offset=offset,
            filters_applied={"centro_costo": centro_costo}
        )
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/lider/{np_lider}", response_model=ColaboradoresListResponseDTO, summary="Por líder")
async def get_colaboradores_by_lider(
    np_lider: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(require_admin)
):
    """Lista colaboradores por líder. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.get_colaboradores_by_lider(
            np_lider=np_lider,
            limit=limit,
            offset=offset
        )
        return ColaboradoresListResponseDTO(
            data=result,
            total_records=len(result),
            limit=limit,
            offset=offset,
            filters_applied={"np_lider": np_lider}
        )
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/search", response_model=ColaboradoresListResponseDTO, summary="Buscar por nombre")
async def search_colaboradores_by_name(
    search_data: ColaboradorSearchDTO,
    current_user: CurrentUser = Depends(require_admin)
):
    """Busca colaboradores por nombre. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.search_colaboradores_by_name(
            search_term=search_data.search_term,
            limit=search_data.limit,
            offset=search_data.offset
        )
        return ColaboradoresListResponseDTO(
            data=result,
            total_records=len(result),
            limit=search_data.limit,
            offset=search_data.offset,
            filters_applied={"search_term": search_data.search_term}
        )
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/info", response_model=ColaboradorInfoDTO, summary="Información de la tabla")
async def get_colaboradores_info(current_user: CurrentUser = Depends(require_admin)):
    """Obtiene información de la tabla de colaboradores. Requiere rol ADMIN"""
    try:
        result = await colaboradores_service.get_table_info()
        return ColaboradorInfoDTO(**result)
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
