"""Cliente principal del datawarehouse - Solo lectura"""

import asyncio
from typing import Dict, List, Any, Optional

from sqlalchemy import text

from .connection import dw_connection
from .query_builder import QueryBuilder
from .exceptions import QueryError, TimeoutError, ConnectionError


class DatawarehouseClient:
    """Cliente para consultas de solo lectura al datawarehouse"""
    
    def __init__(self):
        self.query_builder = QueryBuilder()
        # Verificar que la conexión esté disponible
        if dw_connection is None:
            raise ConnectionError("DatawarehouseConnection no inicializada correctamente")
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Ejecuta una query personalizada de solo lectura"""
        
        # Validar seguridad de la query
        self.query_builder.validate_query_security(query)
        
        try:
            async with dw_connection.get_session() as session:
                # Ejecutar con timeout
                result = await asyncio.wait_for(
                    session.execute(text(query), parameters or {}),
                    timeout=60  # Timeout por defecto
                )
                
                # Convertir a lista de diccionarios
                rows = result.fetchall()
                columns = result.keys()
                
                # Limitar resultados
                if len(rows) > QueryBuilder.MAX_RESULTS:
                    raise QueryError(
                        f"Query retornó {len(rows)} filas, máximo permitido: {QueryBuilder.MAX_RESULTS}"
                    )
                
                return [dict(zip(columns, row)) for row in rows]
                
        except asyncio.TimeoutError:
            raise TimeoutError("Query excedió timeout de 60 segundos")
        except Exception as e:
            raise QueryError(f"Error ejecutando query: {str(e)}")
    
    async def query_table(
        self,
        schema: str,
        table: str,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Consulta una tabla específica con filtros"""
        
        # Construir query
        query, parameters = self.query_builder.build_table_query(
            schema=schema,
            table=table,
            columns=columns,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        
        # Ejecutar query
        return await self.execute_query(query, parameters)
    
    async def get_schemas(self) -> List[str]:
        """Obtiene lista de esquemas disponibles"""
        query = self.query_builder.build_schema_info_query()
        result = await self.execute_query(query)
        return [row['schema_name'] for row in result]
    
    async def get_tables(self, schema: str) -> List[Dict[str, str]]:
        """Obtiene lista de tablas en un esquema"""
        query, parameters = self.query_builder.build_tables_info_query(schema)
        result = await self.execute_query(query, parameters)
        return result
    
    async def get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """Obtiene información de columnas de una tabla"""
        query, parameters = self.query_builder.build_columns_info_query(schema, table)
        result = await self.execute_query(query, parameters)
        return result
    
    async def test_connection(self) -> tuple[bool, str]:
        """Prueba la conexión al datawarehouse"""
        return await dw_connection.test_connection()
    
    async def get_table_count(self, schema: str, table: str) -> int:
        """Obtiene el número de registros en una tabla"""
        query, _ = self.query_builder.build_table_query(
            schema=schema,
            table=table,
            columns=["COUNT(*) as total"]
        )
        
        result = await self.execute_query(query)
        return result[0]['total'] if result else 0
    
    async def table_exists(self, schema: str, table: str) -> bool:
        """Verifica si una tabla existe"""
        try:
            tables = await self.get_tables(schema)
            return any(t['table_name'] == table for t in tables)
        except Exception:
            return False


# Instancia global del cliente
try:
    dw_client = DatawarehouseClient()
except Exception as e:
    print(f"Warning: Error inicializando DatawarehouseClient: {e}")
    dw_client = None
