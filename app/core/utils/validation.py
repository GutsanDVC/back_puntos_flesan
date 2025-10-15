"""Utilidades para validación de datos"""

import re
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.core.exceptions import ValidationError


def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(uuid_str: str) -> bool:
    """Valida formato de UUID"""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Valida que los campos requeridos estén presentes"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Campos requeridos faltantes: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )


def validate_string_length(
    value: str, 
    field_name: str, 
    min_length: Optional[int] = None, 
    max_length: Optional[int] = None
) -> None:
    """Valida la longitud de un string"""
    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"{field_name} debe tener al menos {min_length} caracteres",
            details={"field": field_name, "min_length": min_length, "actual_length": len(value)}
        )
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"{field_name} no puede tener más de {max_length} caracteres",
            details={"field": field_name, "max_length": max_length, "actual_length": len(value)}
        )


def validate_positive_number(value: float, field_name: str) -> None:
    """Valida que un número sea positivo"""
    if value <= 0:
        raise ValidationError(
            f"{field_name} debe ser un número positivo",
            details={"field": field_name, "value": value}
        )


def validate_range(
    value: float, 
    field_name: str, 
    min_value: Optional[float] = None, 
    max_value: Optional[float] = None
) -> None:
    """Valida que un valor esté dentro de un rango"""
    if min_value is not None and value < min_value:
        raise ValidationError(
            f"{field_name} debe ser mayor o igual a {min_value}",
            details={"field": field_name, "min_value": min_value, "actual_value": value}
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field_name} debe ser menor o igual a {max_value}",
            details={"field": field_name, "max_value": max_value, "actual_value": value}
        )


def sanitize_string(value: str) -> str:
    """Sanitiza un string removiendo caracteres peligrosos"""
    # Remover caracteres de control y espacios extra
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    return sanitized.strip()


def validate_phone_number(phone: str) -> bool:
    """Valida formato de número telefónico (formato internacional)"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))


def validate_not_empty_string(value: str, field_name: str) -> None:
    """Valida que un string no esté vacío"""
    if not value or not value.strip():
        raise ValidationError(
            f"{field_name} no puede estar vacío",
            details={"field": field_name}
        )
