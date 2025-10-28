"""Servicio de negocio para canjes de puntos - Consolida lógica de aplicación"""

from datetime import datetime, timezone
from math import ceil
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.repositories.canje_repository import CanjeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.beneficio_repository import BeneficioRepository


class CanjeService:
    """Servicio de negocio para operaciones de canjes de puntos"""
    
    def __init__(
        self,
        canje_repository: CanjeRepository,
        user_repository: UserRepository,
        beneficio_repository: BeneficioRepository
    ):
        self.canje_repository = canje_repository
        self.user_repository = user_repository
        self.beneficio_repository = beneficio_repository
    
    def _to_naive_utc(self, dt: datetime) -> datetime:
        """Normaliza un datetime a UTC sin tzinfo (naive) para almacenamiento consistente"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    
    async def _obtener_dias_vacaciones_acumulados(self, user_id: int) -> int:
        """
        Obtiene los días de vacaciones acumulados del usuario desde el datawarehouse
        
        TODO: Implementar integración real con datawarehouse
        Por ahora retorna un valor mock para testing
        """
        # MOCK - Simulación de consulta al datawarehouse
        # En producción, esto debería consultar la tabla correspondiente
        dias_acumulados = 15  # Valor mock
        
        return dias_acumulados
    
    async def crear_canje(
        self,
        user_id: int,
        beneficio_id: UUID,
        puntos_utilizar: int,
        fecha_canje: datetime,
        fecha_uso: datetime,
        observaciones: Optional[str] = None
    ) -> dict:
        """
        Crea un nuevo canje de puntos con todas las validaciones de negocio
        
        Validaciones:
        - Usuario existe y está activo
        - Beneficio existe y está activo
        - Usuario tiene puntos suficientes
        - Puntos a utilizar <= valor del beneficio
        - Fecha de uso > fecha de canje
        - Usuario no tiene más de 30 días de vacaciones acumulados
        """
        
        # 1. Validar que el usuario existe y está activo
        user = await self.user_repository.get_by_user_id(user_id)
        if not user:
            raise NotFoundError(f"Usuario con user_id {user_id} no encontrado")
        
        if not user.get("is_active", False):
            raise ValidationError(f"El usuario {user_id} está inactivo y no puede realizar canjes")
        
        # 2. Validar que el beneficio existe y está activo
        beneficio = await self.beneficio_repository.get_by_id(beneficio_id)
        if not beneficio:
            raise NotFoundError(f"Beneficio con ID {beneficio_id} no encontrado")
        
        if not beneficio.get("is_active", False):
            raise ValidationError(f"El beneficio {beneficio_id} está inactivo y no puede ser canjeado")
        
        # 3. Validar que el usuario tiene puntos suficientes
        puntos_disponibles = user.get("puntos", 0)
        if puntos_disponibles < puntos_utilizar:
            raise ValidationError(
                f"Puntos insuficientes. Disponible: {puntos_disponibles}, "
                f"Requerido: {puntos_utilizar}"
            )
        
        # 4. Validar que los puntos a utilizar no excedan el valor del beneficio
        valor_beneficio = beneficio.get("valor", 0)
        if puntos_utilizar > valor_beneficio:
            raise ValidationError(
                f"Los puntos a utilizar ({puntos_utilizar}) no pueden ser mayores "
                f"al valor del beneficio ({valor_beneficio})"
            )
        
        # Normalizar fechas a UTC naive para evitar conflictos aware/naive
        fecha_canje_norm = self._to_naive_utc(fecha_canje)
        fecha_uso_norm = self._to_naive_utc(fecha_uso)
        
        # 5. Validar que la fecha de uso sea posterior a la fecha de canje
        if fecha_uso_norm <= fecha_canje_norm:
            raise ValidationError(
                "La fecha de uso debe ser posterior a la fecha de canje"
            )
        
        # 6. Validar días de vacaciones acumulados (máximo 30 días)
        dias_vacaciones = await self._obtener_dias_vacaciones_acumulados(user_id)
        if dias_vacaciones > 30:
            raise ValidationError(
                f"El usuario tiene {dias_vacaciones} días de vacaciones acumulados. "
                f"El máximo permitido es 30 días. No puede realizar canjes hasta regularizar."
            )
        
        # 7. Crear el registro del canje
        canje = await self.canje_repository.create(
            user_id=user_id,
            beneficio_id=beneficio_id,
            puntos_canjeados=puntos_utilizar,
            fecha_canje=fecha_canje_norm,
            fecha_uso=fecha_uso_norm,
            observaciones=observaciones
        )
        
        # 8. Descontar los puntos al usuario
        nuevos_puntos = puntos_disponibles - puntos_utilizar
        await self.user_repository.update(
            user_id=user_id,
            puntos=nuevos_puntos
        )
        
        # 9. Agregar información adicional a la respuesta
        canje["puntos_restantes"] = nuevos_puntos
        
        return canje
    
    async def get_canje_by_id(self, canje_id: UUID) -> dict:
        """Obtiene un canje por ID"""
        canje = await self.canje_repository.get_by_id(canje_id)
        if not canje:
            raise NotFoundError(f"Canje con ID {canje_id} no encontrado")
        
        # Obtener puntos actuales del usuario para incluir en respuesta
        user = await self.user_repository.get_by_user_id(canje["user_id"])
        canje["puntos_restantes"] = user.get("puntos", 0) if user else 0
        
        return canje
    
    async def get_canjes_by_user(
        self,
        user_id: int,
        page: int = 1,
        size: int = 10,
        estado: Optional[str] = None
    ) -> dict:
        """
        Obtiene los canjes de un usuario con paginación
        
        Returns:
            dict con keys: canjes, total, page, size, total_pages
        """
        # Calcular offset
        skip = (page - 1) * size
        
        # Obtener canjes y total
        canjes = await self.canje_repository.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=size,
            estado=estado
        )
        
        total = await self.canje_repository.count_by_user_id(
            user_id=user_id,
            estado=estado
        )
        
        total_pages = ceil(total / size) if total > 0 else 0
        
        # Agregar puntos restantes a cada canje
        user = await self.user_repository.get_by_user_id(user_id)
        puntos_actuales = user.get("puntos", 0) if user else 0
        
        for canje in canjes:
            canje["puntos_restantes"] = puntos_actuales
        
        return {
            "canjes": canjes,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }
    
    async def list_canjes(
        self,
        page: int = 1,
        size: int = 10,
        user_id: Optional[int] = None,
        beneficio_id: Optional[UUID] = None,
        estado: Optional[str] = None
    ) -> dict:
        """
        Lista todos los canjes con paginación y filtros
        
        Returns:
            dict con keys: canjes, total, page, size, total_pages
        """
        # Calcular offset
        skip = (page - 1) * size
        
        # Obtener canjes y total
        canjes = await self.canje_repository.list_canjes(
            skip=skip,
            limit=size,
            user_id=user_id,
            beneficio_id=beneficio_id,
            estado=estado
        )
        
        total = await self.canje_repository.count_canjes(
            user_id=user_id,
            beneficio_id=beneficio_id,
            estado=estado
        )
        
        total_pages = ceil(total / size) if total > 0 else 0
        
        # Agregar puntos restantes (0 por defecto si no se puede obtener)
        for canje in canjes:
            canje["puntos_restantes"] = 0
        
        return {
            "canjes": canjes,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        }
    
    async def actualizar_estado_canje(
        self,
        canje_id: UUID,
        estado: str,
        observaciones: Optional[str] = None
    ) -> dict:
        """
        Actualiza el estado de un canje
        
        Estados permitidos: ACTIVO, USADO, CANCELADO, VENCIDO
        """
        # Validar que el canje existe
        canje = await self.get_canje_by_id(canje_id)
        
        # Validar estado
        estados_validos = ["ACTIVO", "USADO", "CANCELADO", "VENCIDO"]
        if estado not in estados_validos:
            raise ValidationError(
                f"Estado inválido. Estados permitidos: {', '.join(estados_validos)}"
            )
        
        # Si se cancela un canje ACTIVO, devolver los puntos al usuario
        if estado == "CANCELADO" and canje["estado"] == "ACTIVO":
            user = await self.user_repository.get_by_user_id(canje["user_id"])
            if user:
                nuevos_puntos = user.get("puntos", 0) + canje["puntos_canjeados"]
                await self.user_repository.update(
                    user_id=UUID(user["id"]) if isinstance(user["id"], str) else user["id"],
                    puntos=nuevos_puntos
                )
        
        # Actualizar estado
        canje_actualizado = await self.canje_repository.update_estado(
            canje_id=canje_id,
            estado=estado,
            observaciones=observaciones
        )
        
        # Obtener puntos actuales del usuario
        user = await self.user_repository.get_by_user_id(canje_actualizado["user_id"])
        canje_actualizado["puntos_restantes"] = user.get("puntos", 0) if user else 0
        
        return canje_actualizado
