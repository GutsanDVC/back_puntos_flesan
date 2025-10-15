"""Utilidades para manejo de fechas"""

from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Obtiene la fecha y hora actual en UTC"""
    return datetime.now(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """Convierte una fecha a UTC"""
    if dt.tzinfo is None:
        # Si no tiene timezone, asumimos que es UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formatea una fecha como string"""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parsea un string a datetime"""
    return datetime.strptime(date_str, format_str)


def datetime_to_iso(dt: datetime) -> str:
    """Convierte datetime a formato ISO 8601"""
    return dt.isoformat()


def iso_to_datetime(iso_str: str) -> datetime:
    """Convierte string ISO 8601 a datetime"""
    return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))


def is_past(dt: datetime) -> bool:
    """Verifica si una fecha es del pasado"""
    return dt < utc_now()


def is_future(dt: datetime) -> bool:
    """Verifica si una fecha es del futuro"""
    return dt > utc_now()


def days_between(start: datetime, end: datetime) -> int:
    """Calcula los días entre dos fechas"""
    return (end - start).days
