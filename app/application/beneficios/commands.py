"""Comandos para la aplicación de beneficios"""

from datetime import datetime
from uuid import UUID, uuid4

from app.application.beneficios.dto import CreateBeneficioDTO, UpdateBeneficioDTO
from app.application.beneficios.ports import BeneficioRepositoryPort
from app.core.exceptions import BaseAppException
from app.core.security import CurrentUser
from app.domain.beneficios.entities.beneficio import Beneficio
from app.domain.beneficios.services.beneficio_service import BeneficioService


class CreateBeneficioCommand:
    """Comando para crear beneficio"""
    
    def __init__(self, repository: BeneficioRepositoryPort):
        self.repository = repository
    
    async def execute(self, dto: CreateBeneficioDTO, current_user: CurrentUser) -> Beneficio:
        """Ejecuta la creación de beneficio"""
        try:
            # Validar que la imagen esté presente
            if not dto.imagen:
                raise BaseAppException(
                    message="La imagen es requerida para crear un beneficio",
                    error_code="BENEFICIO-ERR-007",
                    details={"field": "imagen"}
                )
            
            # Verificar si ya existe un beneficio con el mismo nombre
            existing = await self.repository.get_by_name(dto.beneficio)
            if existing:
                raise BaseAppException(
                    message=f"Ya existe un beneficio con el nombre '{dto.beneficio}'",
                    error_code="BENEFICIO-ERR-001",
                    details={"beneficio": dto.beneficio}
                )
            
            # Crear entidad de dominio
            beneficio = Beneficio(
                id=uuid4(),
                imagen=dto.imagen,
                beneficio=dto.beneficio,
                detalle=dto.detalle,
                regla1=dto.regla1,
                regla2=dto.regla2,
                valor=dto.valor,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            # Guardar en repositorio
            return await self.repository.create(beneficio)
            
        except ValueError as e:
            raise BaseAppException(
                message=str(e),
                error_code="BENEFICIO-ERR-002",
                details={"validation_error": str(e)}
            )
        except Exception as e:
            raise BaseAppException(
                message="Error interno al crear beneficio",
                error_code="BENEFICIO-ERR-003",
                details={"internal_error": str(e)}
            )


class UpdateBeneficioCommand:
    """Comando para actualizar beneficio"""
    
    def __init__(self, repository: BeneficioRepositoryPort):
        self.repository = repository
    
    async def execute(
        self, 
        beneficio_id: UUID, 
        dto: UpdateBeneficioDTO, 
        current_user: CurrentUser
    ) -> Beneficio:
        """Ejecuta la actualización de beneficio"""
        try:
            # Obtener beneficio existente
            beneficio = await self.repository.get_by_id(beneficio_id)
            if not beneficio:
                raise BaseAppException(
                    message=f"Beneficio con ID {beneficio_id} no encontrado",
                    error_code="BENEFICIO-ERR-004",
                    details={"beneficio_id": str(beneficio_id)}
                )
            
            # Verificar nombre único si se está actualizando
            if dto.beneficio and dto.beneficio != beneficio.beneficio:
                existing = await self.repository.get_by_name(dto.beneficio)
                if existing and existing.id != beneficio_id:
                    raise BaseAppException(
                        message=f"Ya existe un beneficio con el nombre '{dto.beneficio}'",
                        error_code="BENEFICIO-ERR-001",
                        details={"beneficio": dto.beneficio}
                    )
            
            # Actualizar campos si se proporcionan
            if dto.imagen is not None:
                beneficio.imagen = dto.imagen
            if dto.beneficio is not None:
                beneficio.beneficio = dto.beneficio
            if dto.detalle is not None:
                beneficio.detalle = dto.detalle
            if dto.regla1 is not None:
                beneficio.regla1 = dto.regla1
            if dto.regla2 is not None:
                beneficio.regla2 = dto.regla2
            if dto.valor is not None:
                beneficio.valor = dto.valor
            
            beneficio.updated_at = datetime.utcnow()
            
            # Guardar cambios
            return await self.repository.update(beneficio)
            
        except BaseAppException:
            raise
        except ValueError as e:
            raise BaseAppException(
                message=str(e),
                error_code="BENEFICIO-ERR-002",
                details={"validation_error": str(e)}
            )
        except Exception as e:
            raise BaseAppException(
                message="Error interno al actualizar beneficio",
                error_code="BENEFICIO-ERR-005",
                details={"internal_error": str(e)}
            )


class DeactivateBeneficioCommand:
    """Comando para desactivar beneficio"""
    
    def __init__(self, repository: BeneficioRepositoryPort):
        self.repository = repository
    
    async def execute(self, beneficio_id: UUID, current_user: CurrentUser) -> Beneficio:
        """Ejecuta la desactivación de beneficio"""
        try:
            # Obtener beneficio existente
            beneficio = await self.repository.get_by_id(beneficio_id)
            if not beneficio:
                raise BaseAppException(
                    message=f"Beneficio con ID {beneficio_id} no encontrado",
                    error_code="BENEFICIO-ERR-004",
                    details={"beneficio_id": str(beneficio_id)}
                )
            
            # Desactivar beneficio
            beneficio.deactivate()
            beneficio.updated_at = datetime.utcnow()
            
            # Guardar cambios
            return await self.repository.update(beneficio)
            
        except BaseAppException:
            raise
        except Exception as e:
            raise BaseAppException(
                message="Error interno al desactivar beneficio",
                error_code="BENEFICIO-ERR-006",
                details={"internal_error": str(e)}
            )
