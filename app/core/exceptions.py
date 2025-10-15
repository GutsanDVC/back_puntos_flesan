"""Excepciones personalizadas del dominio y aplicación"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Excepción base para todas las excepciones de la aplicación"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class BusinessRuleException(BaseAppException):
    """Excepción para violaciones de reglas de negocio"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP-ERR-001",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class InfrastructureError(BaseAppException):
    """Excepción para errores de infraestructura"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP-ERR-002",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuthenticationError(BaseAppException):
    """Excepción para errores de autenticación"""
    
    def __init__(
        self,
        message: str = "No autenticado",
        error_code: str = "APP-ERR-003",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class AuthorizationError(BaseAppException):
    """Excepción para errores de autorización"""
    
    def __init__(
        self,
        message: str = "No autorizado",
        error_code: str = "APP-ERR-004",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class ValidationError(BaseAppException):
    """Excepción para errores de validación"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "APP-ERR-005",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)


class NotFoundError(BaseAppException):
    """Excepción para recursos no encontrados"""
    
    def __init__(
        self,
        message: str = "Recurso no encontrado",
        error_code: str = "APP-ERR-006",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, details)
