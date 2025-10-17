"""Endpoints REST básicos para consultas al datawarehouse"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.application.datawarehouse.services.datawarehouse_service import datawarehouse_service
from app.infrastructure.auth.dependencies import require_admin
from app.infrastructure.datawarehouse.exceptions import DatawarehouseException
from app.core.security import CurrentUser

router = APIRouter(prefix="/datawarehouse", tags=["Datawarehouse"])


class CustomQueryRequest(BaseModel):
    """Request para query personalizada"""
    query: str
    parameters: Optional[Dict[str, Any]] = None


class TableQueryRequest(BaseModel):
    """Request para consulta de tabla"""
    schema: str
    table: str
    columns: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    order_by: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


@router.get("/test-connection")
async def test_connection(
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Prueba la conexión al datawarehouse
    
    **Requiere:** Rol ADMIN
    """
    try:
        result = await datawarehouse_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/test-connection-debug")
async def test_connection_debug():
    """
    Prueba la conexión al datawarehouse sin autenticación (solo para debug)
    
    **TEMPORAL:** Para debugging - remover en producción
    """
    try:
        result = await datawarehouse_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/config-info")
async def get_config_info(
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Obtiene información de configuración del datawarehouse (sin credenciales)
    
    **Requiere:** Rol ADMIN
    """
    from app.core.config import settings
    
    # Información segura (sin credenciales)
    config_info = {
        "db_host": settings.DB_HOST_DW,
        "db_port": settings.DB_PORT_DW,
        "db_name": settings.DB_NAME_DW,
        "db_driver": settings.DB_DRIVER_DW,
        "has_user": bool(settings.DB_USER_DW),
        "has_password": bool(settings.DB_PASSWORD_DW),
        "database_url_configured": bool(settings.DATABASE_URL_DW)
    }
    
    return {"config": config_info}


@router.get("/schemas")
async def get_schemas(
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Obtiene lista de esquemas disponibles
    
    **Requiere:** Rol ADMIN
    """
    try:
        schemas = await datawarehouse_service.get_available_schemas()
        return {"schemas": schemas}
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/schemas/{schema}/tables")
async def get_tables(
    schema: str,
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Obtiene tablas de un esquema
    
    **Requiere:** Rol ADMIN
    """
    try:
        tables = await datawarehouse_service.get_schema_tables(schema)
        return {"schema": schema, "tables": tables}
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/schemas/{schema}/tables/{table}")
async def get_table_structure(
    schema: str,
    table: str,
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Obtiene estructura de una tabla
    
    **Requiere:** Rol ADMIN
    """
    try:
        structure = await datawarehouse_service.get_table_structure(schema, table)
        return structure
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/query/custom")
async def execute_custom_query(
    request: CustomQueryRequest,
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Ejecuta una query personalizada al datawarehouse
    
    **Requiere:** Rol ADMIN
    **Restricciones:** Solo queries SELECT
    """
    try:
        result = await datawarehouse_service.execute_custom_query(
            query=request.query,
            parameters=request.parameters
        )
        
        return {
            "data": result,
            "total_rows": len(result)
        }
        
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/query/table")
async def query_table(
    request: TableQueryRequest,
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Consulta una tabla específica del datawarehouse
    
    **Requiere:** Rol ADMIN
    """
    try:
        result = await datawarehouse_service.query_table(
            schema=request.schema,
            table=request.table,
            columns=request.columns,
            filters=request.filters,
            order_by=request.order_by,
            limit=request.limit,
            offset=request.offset
        )
        
        return {
            "data": result,
            "total_rows": len(result)
        }
        
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
