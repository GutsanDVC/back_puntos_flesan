"""Constructor y validador de queries para datawarehouse"""

import re
from typing import Dict, List, Any, Optional

from .exceptions import SecurityError, InvalidSchemaError, InvalidTableError


class QueryBuilder:
    """Constructor y validador de queries de solo lectura"""
    
    # Patrones de seguridad
    FORBIDDEN_KEYWORDS = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]
    
    # Patrón para validar nombres de esquema/tabla (solo alfanuméricos y _)
    NAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    
    # Límite máximo de resultados por defecto
    MAX_RESULTS = 1000
    
    @classmethod
    def validate_query_security(cls, query: str) -> None:
        """Valida que la query sea segura (solo SELECT)"""
        query_upper = query.upper().strip()
        
        # Verificar que empiece con SELECT
        if not query_upper.startswith('SELECT'):
            raise SecurityError("Solo se permiten queries SELECT")
        
        # Verificar que no contenga palabras prohibidas
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                raise SecurityError(f"Palabra prohibida encontrada: {keyword}")
        
        # Verificar patrones de SQL injection básicos
        dangerous_patterns = [
            r';\s*(DROP|DELETE|UPDATE|INSERT)',
            r'--\s*\w',  # Comentarios sospechosos
            r'/\*.*\*/',  # Comentarios de bloque
            r'UNION\s+SELECT.*FROM',  # UNION injection
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                raise SecurityError("Patrón de SQL injection detectado")
    
    @classmethod
    def validate_name(cls, name: str, name_type: str = "nombre") -> None:
        """Valida nombres de esquema/tabla"""
        if not name or not isinstance(name, str):
            raise InvalidSchemaError(f"{name_type} no puede estar vacío")
        
        if not cls.NAME_PATTERN.match(name):
            raise InvalidSchemaError(
                f"{name_type} solo puede contener letras, números y guiones bajos"
            )
        
        if len(name) > 63:  # Límite de PostgreSQL
            raise InvalidSchemaError(f"{name_type} demasiado largo (máximo 63 caracteres)")
    
    @classmethod
    def build_table_query(
        cls,
        schema: str,
        table: str,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Construye una query SELECT para una tabla específica"""
        
        # Validar nombres
        cls.validate_name(schema, "esquema")
        cls.validate_name(table, "tabla")
        
        # Construir SELECT
        if columns:
            # Validar nombres de columnas
            for col in columns:
                cls.validate_name(col, "columna")
            columns_str = ", ".join(columns)
        else:
            columns_str = "*"
        
        # Query base
        query = f"SELECT {columns_str} FROM {schema}.{table}"
        parameters = {}
        
        # Agregar filtros WHERE
        if filters:
            where_conditions = []
            for i, (column, value) in enumerate(filters.items()):
                cls.validate_name(column, "columna de filtro")
                param_name = f"filter_{i}"
                where_conditions.append(f"{column} = :{param_name}")
                parameters[param_name] = value
            
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
        
        # Agregar ORDER BY
        if order_by:
            cls.validate_name(order_by, "columna de ordenamiento")
            query += f" ORDER BY {order_by}"
        
        # Agregar LIMIT y OFFSET con límite máximo
        if limit:
            limit = min(int(limit), cls.MAX_RESULTS)
            query += f" LIMIT {limit}"
        else:
            # Límite por defecto para evitar queries muy grandes
            query += f" LIMIT {cls.MAX_RESULTS}"
        
        if offset:
            query += f" OFFSET {int(offset)}"
        
        return query, parameters
    
    @classmethod
    def build_schema_info_query(cls) -> str:
        """Query para obtener esquemas disponibles"""
        return """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY schema_name
        """
    
    @classmethod
    def build_tables_info_query(cls, schema: str) -> tuple[str, Dict[str, Any]]:
        """Query para obtener tablas de un esquema"""
        cls.validate_name(schema, "esquema")
        
        query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = :schema
        ORDER BY table_name
        """
        
        return query, {"schema": schema}
    
    @classmethod
    def build_columns_info_query(cls, schema: str, table: str) -> tuple[str, Dict[str, Any]]:
        """Query para obtener columnas de una tabla"""
        cls.validate_name(schema, "esquema")
        cls.validate_name(table, "tabla")
        
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_schema = :schema AND table_name = :table
        ORDER BY ordinal_position
        """
        
        return query, {"schema": schema, "table": table}
