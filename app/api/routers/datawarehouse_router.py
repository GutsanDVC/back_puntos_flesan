"""Router de consultas al datawarehouse"""

from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

# TODO: Migrar servicios de datawarehouse
# from app.application.datawarehouse.services.datawarehouse_service import datawarehouse_service
# from app.infrastructure.datawarehouse.exceptions import DatawarehouseException

from app.core.config import settings
from app.core.security import CurrentUser
from app.core.auth import require_admin


router = APIRouter(prefix="/datawarehouse", tags=["datawarehouse"])


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


@router.get("/test-connection", summary="Probar conexión al datawarehouse")
async def test_connection(current_user: CurrentUser = Depends(require_admin)):
    """Prueba la conexión al datawarehouse. Requiere rol ADMIN"""
    try:
        result = await datawarehouse_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/config-info", summary="Información de configuración")
async def get_config_info(current_user: CurrentUser = Depends(require_admin)):
    """Obtiene información de configuración del datawarehouse (sin credenciales). Requiere rol ADMIN"""
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


@router.get("/schemas", summary="Listar esquemas disponibles")
async def get_schemas(current_user: CurrentUser = Depends(require_admin)):
    """Obtiene lista de esquemas disponibles. Requiere rol ADMIN"""
    try:
        schemas = await datawarehouse_service.get_available_schemas()
        return {"schemas": schemas}
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/schemas/{schema}/tables", summary="Listar tablas de un esquema")
async def get_tables(
    schema: str,
    current_user: CurrentUser = Depends(require_admin)
):
    """Obtiene tablas de un esquema. Requiere rol ADMIN"""
    try:
        tables = await datawarehouse_service.get_schema_tables(schema)
        return {"schema": schema, "tables": tables}
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/schemas/{schema}/tables/{table}", summary="Estructura de tabla")
async def get_table_structure(
    schema: str,
    table: str,
    current_user: CurrentUser = Depends(require_admin)
):
    """Obtiene estructura de una tabla. Requiere rol ADMIN"""
    try:
        structure = await datawarehouse_service.get_table_structure(schema, table)
        return structure
    except DatawarehouseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.post("/query/custom", summary="Ejecutar query personalizada")
async def execute_custom_query(
    request: CustomQueryRequest,
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Ejecuta una query personalizada al datawarehouse.
    Requiere rol ADMIN.
    Restricción: Solo queries SELECT
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


@router.post("/query/table", summary="Consultar tabla")
async def query_table(
    request: TableQueryRequest,
    current_user: CurrentUser = Depends(require_admin)
):
    """Consulta una tabla específica del datawarehouse. Requiere rol ADMIN"""
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
