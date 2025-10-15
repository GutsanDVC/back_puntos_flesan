"""Configuración de logging con formato JSON y trazabilidad"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import settings

# Context variables para trazabilidad
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs estructurados"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": trace_id_var.get(),
            "user_id": user_id_var.get(),
        }
        
        # Agregar información adicional si está disponible
        if hasattr(record, 'path'):
            log_entry['path'] = record.path
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'latency'):
            log_entry['latency'] = record.latency
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
            
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging() -> None:
    """Configura el sistema de logging de la aplicación"""
    
    # Configurar el logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Limpiar handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Crear handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    
    # Configurar loggers específicos
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado"""
    return logging.getLogger(name)


def set_trace_id(trace_id: Optional[str] = None) -> str:
    """Establece el trace_id para el contexto actual"""
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    trace_id_var.set(trace_id)
    return trace_id


def set_user_id(user_id: Optional[str]) -> None:
    """Establece el user_id para el contexto actual"""
    user_id_var.set(user_id)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    latency: float,
    extra_data: Optional[Dict[str, Any]] = None
) -> None:
    """Log estructurado para requests HTTP"""
    logger.info(
        f"{method} {path} - {status_code}",
        extra={
            'method': method,
            'path': path,
            'status_code': status_code,
            'latency': latency,
            'extra_data': extra_data or {}
        }
    )
