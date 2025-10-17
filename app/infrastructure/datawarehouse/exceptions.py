"""Excepciones específicas del módulo de datawarehouse"""

from typing import Any, Dict, Optional
from app.core.exceptions import BaseAppException


class DatawarehouseException(BaseAppException):
    """Excepción base del datawarehouse"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-001",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ConnectionError(DatawarehouseException):
    """Error de conexión al datawarehouse"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-002",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class QueryError(DatawarehouseException):
    """Error en la ejecución de query"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-003",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class SecurityError(DatawarehouseException):
    """Error de seguridad en query (no SELECT, SQL injection, etc.)"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-004",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class TimeoutError(DatawarehouseException):
    """Error de timeout en consulta"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-005",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class InvalidSchemaError(DatawarehouseException):
    """Esquema no válido o no existe"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-006",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class InvalidTableError(DatawarehouseException):
    """Tabla no válida o no existe"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DW-ERR-007",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
