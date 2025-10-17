"""Servicio para gestionar consultas de colaboradores desde el datawarehouse"""

from typing import Dict, List, Any, Optional
from datetime import date

from app.infrastructure.datawarehouse.client import dw_client
from app.infrastructure.datawarehouse.exceptions import DatawarehouseException


class ColaboradoresService:
    """Servicio para consultas de colaboradores desde sap_maestro_colaborador"""
    
    SCHEMA = "flesan_rrhh"
    TABLE = "sap_maestro_colaborador"
    
    # Campos disponibles para filtros
    FILTERABLE_FIELDS = {
        "empl_status",
        "user_id", 
        "national_id",
        "first_name",
        "last_name",
        "correo_flesan",
        "centro_costo",
        "external_cod_cargo",
        "fecha_ingreso",
        "external_cod_tipo_contrato",
        "np_lider"
    }
    
    # Campos principales para consultas (basado en el diagrama de la tabla)
    DEFAULT_COLUMNS = [
        "user_id",
        "empl_status", 
        "first_name",
        "last_name",
        "second_last_name",
        "middle_name",
        "national_id",
        "correo_flesan",
        "correo_gmail",
        "run",
        "empresa",
        "centro_costo",
        "external_cod_cargo",
        "fecha_ingreso",
        "ubicacion",
        "nombre_centro_costo",
        "departamento",
        "nombre_departamento",
        "division",
        "nombre_division",
        "external_cod_tipo_contrato",
        "fecha_fin_contrato",
        "fecha_termino",
        "forma_pago",
        "np_lider",
        "fecha_antiguedad",
        "fecha_registro_termino",
        "id_clasificacion_gasto",
        "tipo_gasto",
        "horario",
        "genero",
        "pais",
        "eventreason",
        "fecha_nacimiento"
    ]
    
    def __init__(self):
        if dw_client is None:
            raise DatawarehouseException("Cliente de datawarehouse no disponible")
        self.client = dw_client
    
    
    async def get_colaboradores(
        self,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene lista de colaboradores con filtros
        
        Args:
            filters: Filtros a aplicar (solo campos permitidos)
            columns: Columnas a seleccionar (None = columnas por defecto)
            order_by: Campo para ordenar
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de colaboradores
        """
        # Validar filtros permitidos
        if filters:
            invalid_filters = set(filters.keys()) - self.FILTERABLE_FIELDS
            if invalid_filters:
                raise DatawarehouseException(
                    f"Filtros no permitidos: {', '.join(invalid_filters)}. "
                    f"Filtros válidos: {', '.join(sorted(self.FILTERABLE_FIELDS))}"
                )
        
        # Usar columnas por defecto si no se especifican
        if columns is None:
            columns = self.DEFAULT_COLUMNS
        
        return await self.client.query_table(
            schema=self.SCHEMA,
            table=self.TABLE,
            columns=columns,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
    
    async def get_colaborador_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un colaborador específico por user_id
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Datos del colaborador o None si no existe
        """
        result = await self.get_colaboradores(
            filters={"user_id": user_id},
            limit=1
        )
        return result[0] if result else None
    
    async def get_colaborador_by_national_id(self, national_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un colaborador específico por cédula nacional
        
        Args:
            national_id: Cédula nacional
            
        Returns:
            Datos del colaborador o None si no existe
        """
        result = await self.get_colaboradores(
            filters={"national_id": national_id},
            limit=1
        )
        return result[0] if result else None
    
    async def get_colaboradores_activos(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene colaboradores con estado activo
        
        Args:
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de colaboradores activos
        """
        return await self.get_colaboradores(
            filters={"empl_status": "A"},  # Asumiendo que 'A' es activo
            limit=limit,
            offset=offset
        )
    
    async def get_colaboradores_by_centro_costo(
        self,
        centro_costo: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene colaboradores por centro de costo
        
        Args:
            centro_costo: Código del centro de costo
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de colaboradores del centro de costo
        """
        return await self.get_colaboradores(
            filters={"centro_costo": centro_costo},
            limit=limit,
            offset=offset
        )
    
    async def get_colaboradores_by_lider(
        self,
        np_lider: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene colaboradores por líder
        
        Args:
            np_lider: Nombre del líder
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de colaboradores del líder
        """
        return await self.get_colaboradores(
            filters={"np_lider": np_lider},
            limit=limit,
            offset=offset
        )
    
    async def search_colaboradores_by_name(
        self,
        search_term: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca colaboradores por nombre (first_name o last_name)
        
        Args:
            search_term: Término de búsqueda
            limit: Límite de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de colaboradores que coinciden
        """
        # Para búsqueda por nombre, usamos query personalizada
        query = f"""
        SELECT {', '.join(self.DEFAULT_COLUMNS)}
        FROM {self.SCHEMA}.{self.TABLE}
        WHERE LOWER(first_name) LIKE LOWER(:search_term)
           OR LOWER(last_name) LIKE LOWER(:search_term)
           OR LOWER(second_last_name) LIKE LOWER(:search_term)
        ORDER BY first_name, last_name
        """
        
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        
        return await self.client.execute_query(
            query=query,
            parameters={"search_term": f"%{search_term}%"}
        )
    
    async def get_table_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la tabla de colaboradores
        
        Returns:
            Información de la tabla
        """
        columns = await self.client.get_columns(self.SCHEMA, self.TABLE)
        count = await self.client.get_table_count(self.SCHEMA, self.TABLE)

        return {
            "schema": self.SCHEMA,
            "table": self.TABLE,
            "total_records": count,
            "columns": len(columns),
            "filterable_fields": sorted(list(self.FILTERABLE_FIELDS)),
            "default_columns": self.DEFAULT_COLUMNS
        }


# Instancia del servicio
try:
    colaboradores_service = ColaboradoresService()
except Exception as e:
    print(f"Warning: Error inicializando ColaboradoresService: {e}")
    colaboradores_service = None
