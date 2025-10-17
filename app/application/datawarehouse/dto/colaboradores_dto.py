"""DTOs para consultas de colaboradores"""

from typing import Dict, List, Any, Optional
from datetime import date
from pydantic import BaseModel, Field, validator


class ColaboradorFiltersDTO(BaseModel):
    """DTO para filtros de colaboradores"""
    empl_status: Optional[str] = Field(None, description="Estado del empleado")
    user_id: Optional[int] = Field(None, description="ID del usuario")
    national_id: Optional[str] = Field(None, description="Cédula nacional")
    first_name: Optional[str] = Field(None, description="Primer nombre")
    last_name: Optional[str] = Field(None, description="Apellido paterno")
    correo_flesan: Optional[str] = Field(None, description="Correo corporativo")
    centro_costo: Optional[str] = Field(None, description="Centro de costo")
    external_cod_cargo: Optional[str] = Field(None, description="Código externo del cargo")
    fecha_ingreso: Optional[date] = Field(None, description="Fecha de ingreso")
    external_cod_tipo_contrato: Optional[str] = Field(None, description="Código tipo de contrato")
    np_lider: Optional[str] = Field(None, description="Nombre del líder")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario eliminando valores None"""
        return {k: v for k, v in self.dict().items() if v is not None}


class ColaboradorQueryDTO(BaseModel):
    """DTO para consulta de colaboradores"""
    filters: Optional[ColaboradorFiltersDTO] = Field(None, description="Filtros a aplicar")
    columns: Optional[List[str]] = Field(None, description="Columnas a seleccionar")
    order_by: Optional[str] = Field(None, description="Campo para ordenar")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Límite de resultados")
    offset: Optional[int] = Field(None, ge=0, description="Offset para paginación")
    
    @validator('order_by')
    def validate_order_by(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("order_by solo puede contener letras, números, guiones y guiones bajos")
        return v


class ColaboradorSearchDTO(BaseModel):
    """DTO para búsqueda de colaboradores por nombre"""
    search_term: str = Field(..., min_length=2, description="Término de búsqueda")
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Límite de resultados")
    offset: Optional[int] = Field(0, ge=0, description="Offset para paginación")


class ColaboradorResponseDTO(BaseModel):
    """DTO para respuesta de colaborador individual"""
    user_id: Optional[int]
    empl_status: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    second_last_name: Optional[str]
    middle_name: Optional[str]
    national_id: Optional[str]
    correo_flesan: Optional[str]
    correo_gmail: Optional[str]
    run: Optional[str]
    empresa: Optional[str]
    centro_costo: Optional[str]
    external_cod_cargo: Optional[str]
    fecha_ingreso: Optional[date]
    ubicacion: Optional[str]
    nombre_centro_costo: Optional[str]
    departamento: Optional[str]
    nombre_departamento: Optional[str]
    division: Optional[str]
    nombre_division: Optional[str]
    external_cod_tipo_contrato: Optional[str]
    fecha_fin_contrato: Optional[date]
    fecha_termino: Optional[date]
    forma_pago: Optional[str]
    np_lider: Optional[str]
    fecha_antiguedad: Optional[date]
    fecha_registro_termino: Optional[date]
    id_clasificacion_gasto: Optional[str]
    tipo_gasto: Optional[str]
    horario: Optional[str]
    genero: Optional[str]
    pais: Optional[str]
    dias_nacimiento: Optional[int]
    eventreason: Optional[str]
    fecha_nacimiento: Optional[date]
    
    @property
    def full_name(self) -> str:
        """Nombre completo del colaborador"""
        names = [self.first_name, self.middle_name, self.last_name, self.second_last_name]
        return " ".join([name for name in names if name])
    
    class Config:
        from_attributes = True


class ColaboradoresListResponseDTO(BaseModel):
    """DTO para respuesta de lista de colaboradores"""
    data: List[Dict[str, Any]] = Field(..., description="Lista de colaboradores")
    total_records: int = Field(..., description="Total de registros encontrados")
    limit: Optional[int] = Field(None, description="Límite aplicado")
    offset: Optional[int] = Field(None, description="Offset aplicado")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")


class ColaboradorInfoDTO(BaseModel):
    """DTO para información de la tabla de colaboradores"""
    schema: str = Field(..., description="Esquema de la tabla")
    table: str = Field(..., description="Nombre de la tabla")
    total_records: int = Field(..., description="Total de registros")
    columns: int = Field(..., description="Número de columnas")
    filterable_fields: List[str] = Field(..., description="Campos disponibles para filtros")
    default_columns: List[str] = Field(..., description="Columnas por defecto")
