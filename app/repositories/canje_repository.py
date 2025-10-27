"""Repositorio de canjes - Acceso a datos con SQL RAW"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class CanjeRepository:
    """Repositorio para operaciones de base de datos de canjes usando SQL RAW"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        user_id: int,
        beneficio_id: int,
        puntos_canjeados: int,
        fecha_canje: datetime,
        fecha_uso: datetime,
        observaciones: Optional[str] = None
    ) -> dict:
        """Crea un nuevo registro de canje usando SQL RAW"""
        canje_id = uuid4()
        created_at = datetime.utcnow()
        
        query = text("""
            INSERT INTO puntos_flesan.historial_canjes 
            (id, user_id, beneficio_id, puntos_canjeados, fecha_canje, fecha_uso, 
             estado, observaciones, created_at, updated_at)
            VALUES 
            (:id, :user_id, :beneficio_id, :puntos_canjeados, :fecha_canje, :fecha_uso,
             :estado, :observaciones, :created_at, :updated_at)
            RETURNING id, user_id, beneficio_id, puntos_canjeados, fecha_canje, fecha_uso,
                      estado, observaciones, created_at, updated_at
        """)
        
        result = await self.session.execute(
            query,
            {
                "id": str(canje_id),
                "user_id": user_id,
                "beneficio_id": beneficio_id,
                "puntos_canjeados": puntos_canjeados,
                "fecha_canje": fecha_canje,
                "fecha_uso": fecha_uso,
                "estado": "ACTIVO",
                "observaciones": observaciones,
                "created_at": created_at,
                "updated_at": None
            }
        )
        
        row = result.fetchone()
        return self._row_to_dict(row)
    
    async def get_by_id(self, canje_id: UUID) -> Optional[dict]:
        """Obtiene un canje por ID usando SQL RAW"""
        query = text("""
            SELECT id, user_id, beneficio_id, puntos_canjeados, fecha_canje, fecha_uso,
                   estado, observaciones, created_at, updated_at
            FROM puntos_flesan.historial_canjes
            WHERE id = :canje_id
        """)
        
        result = await self.session.execute(query, {"canje_id": str(canje_id)})
        row = result.fetchone()
        
        return self._row_to_dict(row) if row else None
    
    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        estado: Optional[str] = None
    ) -> List[dict]:
        """Obtiene los canjes de un usuario con paginación usando SQL RAW"""
        where_conditions = ["user_id = :user_id"]
        params = {"user_id": user_id, "skip": skip, "limit": limit}
        
        if estado:
            where_conditions.append("estado = :estado")
            params["estado"] = estado
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = text(f"""
            SELECT id, user_id, beneficio_id, puntos_canjeados, fecha_canje, fecha_uso,
                   estado, observaciones, created_at, updated_at
            FROM puntos_flesan.historial_canjes
            {where_clause}
            ORDER BY fecha_canje DESC
            OFFSET :skip LIMIT :limit
        """)
        
        result = await self.session.execute(query, params)
        rows = result.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    async def count_by_user_id(self, user_id: int, estado: Optional[str] = None) -> int:
        """Cuenta los canjes de un usuario usando SQL RAW"""
        where_conditions = ["user_id = :user_id"]
        params = {"user_id": user_id}
        
        if estado:
            where_conditions.append("estado = :estado")
            params["estado"] = estado
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        query = text(f"""
            SELECT COUNT(id) as total
            FROM puntos_flesan.historial_canjes
            {where_clause}
        """)
        
        result = await self.session.execute(query, params)
        row = result.fetchone()
        return row.total if row else 0
    
    async def list_canjes(
        self,
        skip: int = 0,
        limit: int = 10,
        user_id: Optional[int] = None,
        beneficio_id: Optional[int] = None,
        estado: Optional[str] = None
    ) -> List[dict]:
        """Lista canjes con filtros usando SQL RAW"""
        where_conditions = []
        params = {"skip": skip, "limit": limit}
        
        if user_id:
            where_conditions.append("user_id = :user_id")
            params["user_id"] = user_id
        
        if beneficio_id:
            where_conditions.append("beneficio_id = :beneficio_id")
            params["beneficio_id"] = beneficio_id
        
        if estado:
            where_conditions.append("estado = :estado")
            params["estado"] = estado
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT id, user_id, beneficio_id, puntos_canjeados, fecha_canje, fecha_uso,
                   estado, observaciones, created_at, updated_at
            FROM puntos_flesan.historial_canjes
            {where_clause}
            ORDER BY fecha_canje DESC
            OFFSET :skip LIMIT :limit
        """)
        
        result = await self.session.execute(query, params)
        rows = result.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    async def count_canjes(
        self,
        user_id: Optional[int] = None,
        beneficio_id: Optional[int] = None,
        estado: Optional[str] = None
    ) -> int:
        """Cuenta canjes con filtros usando SQL RAW"""
        where_conditions = []
        params = {}
        
        if user_id:
            where_conditions.append("user_id = :user_id")
            params["user_id"] = user_id
        
        if beneficio_id:
            where_conditions.append("beneficio_id = :beneficio_id")
            params["beneficio_id"] = beneficio_id
        
        if estado:
            where_conditions.append("estado = :estado")
            params["estado"] = estado
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT COUNT(id) as total
            FROM puntos_flesan.historial_canjes
            {where_clause}
        """)
        
        result = await self.session.execute(query, params)
        row = result.fetchone()
        return row.total if row else 0
    
    async def update_estado(
        self,
        canje_id: UUID,
        estado: str,
        observaciones: Optional[str] = None
    ) -> dict:
        """Actualiza el estado de un canje usando SQL RAW"""
        query = text("""
            UPDATE puntos_flesan.historial_canjes
            SET estado = :estado,
                observaciones = COALESCE(:observaciones, observaciones),
                updated_at = :updated_at
            WHERE id = :canje_id
            RETURNING id, user_id, beneficio_id, puntos_canjeados, fecha_canje, fecha_uso,
                      estado, observaciones, created_at, updated_at
        """)
        
        result = await self.session.execute(
            query,
            {
                "canje_id": str(canje_id),
                "estado": estado,
                "observaciones": observaciones,
                "updated_at": datetime.utcnow()
            }
        )
        
        row = result.fetchone()
        return self._row_to_dict(row) if row else None
    
    def _row_to_dict(self, row) -> dict:
        """Convierte una fila de SQL RAW a diccionario"""
        if not row:
            return None
        
        return {
            "id": UUID(row.id) if isinstance(row.id, str) else row.id,
            "user_id": row.user_id,
            "beneficio_id": row.beneficio_id,
            "puntos_canjeados": row.puntos_canjeados,
            "fecha_canje": row.fecha_canje,
            "fecha_uso": row.fecha_uso,
            "estado": row.estado,
            "observaciones": row.observaciones,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }
