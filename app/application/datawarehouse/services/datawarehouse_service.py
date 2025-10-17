"""Servicio de aplicación para consultas al datawarehouse"""

from typing import Dict, List, Any, Optional

from app.infrastructure.datawarehouse.client import dw_client
from app.infrastructure.datawarehouse.exceptions import DatawarehouseException


class DatawarehouseService:
    """Servicio para gestionar consultas al datawarehouse"""
    
    def __init__(self):
        self.client = dw_client
    
    async def execute_custom_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una query personalizada
        
        Args:
            query: Query SQL (solo SELECT)
            parameters: Parámetros para la query
            
        Returns:
            Lista de resultados como diccionarios
            
        Raises:
            DatawarehouseException: Si hay error en la query o conexión
        """
        return await self.client.execute_query(query, parameters)
    
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
        """
        Consulta una tabla específica
        
        Args:
            schema: Nombre del esquema
            table: Nombre de la tabla
            columns: Lista de columnas a seleccionar (None = todas)
            filters: Filtros WHERE como diccionario
            order_by: Columna para ordenar
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de resultados como diccionarios
        """
        return await self.client.query_table(
            schema=schema,
            table=table,
            columns=columns,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
    
    async def get_available_schemas(self) -> List[str]:
        """
        Obtiene lista de esquemas disponibles
        
        Returns:
            Lista de nombres de esquemas
        """
        return await self.client.get_schemas()
    
    async def get_schema_tables(self, schema: str) -> List[Dict[str, str]]:
        """
        Obtiene tablas de un esquema
        
        Args:
            schema: Nombre del esquema
            
        Returns:
            Lista de tablas con información (name, type)
        """
        return await self.client.get_tables(schema)
    
    async def get_table_structure(self, schema: str, table: str) -> Dict[str, Any]:
        """
        Obtiene estructura completa de una tabla
        
        Args:
            schema: Nombre del esquema
            table: Nombre de la tabla
            
        Returns:
            Diccionario con información de la tabla y sus columnas
        """
        columns = await self.client.get_columns(schema, table)
        table_count = await self.client.get_table_count(schema, table)
        
        return {
            "schema": schema,
            "table": table,
            "columns": columns,
            "row_count": table_count,
            "exists": len(columns) > 0
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión al datawarehouse
        
        Returns:
            Diccionario con estado de la conexión
        """
        try:
            is_connected, message = await self.client.test_connection()
            return {
                "connected": is_connected,
                "status": "OK" if is_connected else "ERROR",
                "message": message
            }
        except Exception as e:
            return {
                "connected": False,
                "status": "ERROR",
                "message": f"Error de conexión: {str(e)}"
            }


# Instancia del servicio
datawarehouse_service = DatawarehouseService()
