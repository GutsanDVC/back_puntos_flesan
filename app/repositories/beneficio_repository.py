"""Repositorio de beneficios - Acceso a datos con SQL RAW"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BeneficioRepository:
    """Repositorio para operaciones de base de datos de beneficios usando SQL RAW"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        beneficio: str,
        detalle: str,
        regla1: str,
        regla2: str,
        valor: int,
        imagen: str
    ) -> dict:
        """Crea un nuevo beneficio usando SQL RAW"""
        beneficio_id = uuid4()
        created_at = datetime.utcnow()
        
        query = text("""
            INSERT INTO puntos_flesan.beneficios 
            (id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at)
            VALUES 
            (:id, :imagen, :beneficio, :detalle, :regla1, :regla2, :valor, :is_active, :created_at, :updated_at)
            RETURNING id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at
        """)
        
        result = await self.session.execute(
            query,
            {
                "id": str(beneficio_id),
                "imagen": imagen,
                "beneficio": beneficio,
                "detalle": detalle,
                "regla1": regla1,
                "regla2": regla2,
                "valor": valor,
                "is_active": True,
                "created_at": created_at,
                "updated_at": None
            }
        )
        
        row = result.fetchone()
        return self._row_to_dict(row)
    
    async def get_by_id(self, beneficio_id: UUID) -> Optional[dict]:
        """Obtiene un beneficio por ID usando SQL RAW"""
        query = text("""
            SELECT id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at
            FROM puntos_flesan.beneficios
            WHERE id = :beneficio_id
        """)
        
        result = await self.session.execute(query, {"beneficio_id": str(beneficio_id)})
        row = result.fetchone()
        
        return self._row_to_dict(row) if row else None
    
    async def get_by_name(self, name: str) -> Optional[dict]:
        """Obtiene un beneficio por nombre usando SQL RAW"""
        query = text("""
            SELECT id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at
            FROM puntos_flesan.beneficios
            WHERE LOWER(beneficio) = LOWER(:name)
        """)
        
        result = await self.session.execute(query, {"name": name})
        row = result.fetchone()
        
        return self._row_to_dict(row) if row else None
    
    async def update(
        self,
        beneficio_id: UUID,
        imagen: Optional[str] = None,
        beneficio: Optional[str] = None,
        detalle: Optional[str] = None,
        regla1: Optional[str] = None,
        regla2: Optional[str] = None,
        valor: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """Actualiza un beneficio usando SQL RAW"""
        # Obtener beneficio actual
        current = await self.get_by_id(beneficio_id)
        if not current:
            raise ValueError(f"Beneficio con ID {beneficio_id} no encontrado")
        
        # Preparar valores actualizados
        updated_imagen = imagen if imagen is not None else current["imagen"]
        updated_beneficio = beneficio if beneficio is not None else current["beneficio"]
        updated_detalle = detalle if detalle is not None else current["detalle"]
        updated_regla1 = regla1 if regla1 is not None else current["regla1"]
        updated_regla2 = regla2 if regla2 is not None else current["regla2"]
        updated_valor = valor if valor is not None else current["valor"]
        updated_is_active = is_active if is_active is not None else current["is_active"]
        
        query = text("""
            UPDATE puntos_flesan.beneficios
            SET imagen = :imagen,
                beneficio = :beneficio,
                detalle = :detalle,
                regla1 = :regla1,
                regla2 = :regla2,
                valor = :valor,
                is_active = :is_active,
                updated_at = :updated_at
            WHERE id = :beneficio_id
            RETURNING id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at
        """)
        
        result = await self.session.execute(
            query,
            {
                "beneficio_id": str(beneficio_id),
                "imagen": updated_imagen,
                "beneficio": updated_beneficio,
                "detalle": updated_detalle,
                "regla1": updated_regla1,
                "regla2": updated_regla2,
                "valor": updated_valor,
                "is_active": updated_is_active,
                "updated_at": datetime.utcnow()
            }
        )
        
        row = result.fetchone()
        return self._row_to_dict(row)
    
    async def delete(self, beneficio_id: UUID) -> bool:
        """Elimina un beneficio (soft delete) usando SQL RAW"""
        query = text("""
            UPDATE puntos_flesan.beneficios
            SET is_active = false,
                updated_at = :updated_at
            WHERE id = :beneficio_id
            RETURNING id
        """)
        
        result = await self.session.execute(
            query,
            {
                "beneficio_id": str(beneficio_id),
                "updated_at": datetime.utcnow()
            }
        )
        
        row = result.fetchone()
        return row is not None
    
    async def list_beneficios(
        self,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None
    ) -> List[dict]:
        """Lista beneficios con filtros usando SQL RAW"""
        where_conditions = []
        params = {"skip": skip, "limit": limit}
        
        if is_active is not None:
            where_conditions.append("is_active = :is_active")
            params["is_active"] = is_active
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at
            FROM puntos_flesan.beneficios
            {where_clause}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
        """)
        
        result = await self.session.execute(query, params)
        rows = result.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    async def count_beneficios(self, is_active: Optional[bool] = None) -> int:
        """Cuenta beneficios con filtros usando SQL RAW"""
        where_conditions = []
        params = {}
        
        if is_active is not None:
            where_conditions.append("is_active = :is_active")
            params["is_active"] = is_active
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT COUNT(id) as total
            FROM puntos_flesan.beneficios
            {where_clause}
        """)
        
        result = await self.session.execute(query, params)
        row = result.fetchone()
        return row.total if row else 0
    
    async def search(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[dict]:
        """Busca beneficios por texto usando SQL RAW"""
        query = text("""
            SELECT id, imagen, beneficio, detalle, regla1, regla2, valor, is_active, created_at, updated_at
            FROM puntos_flesan.beneficios
            WHERE 
                LOWER(beneficio) LIKE LOWER(:search_term)
                OR LOWER(detalle) LIKE LOWER(:search_term)
                OR LOWER(regla1) LIKE LOWER(:search_term)
                OR LOWER(regla2) LIKE LOWER(:search_term)
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
        """)
        
        search_pattern = f"%{search_term}%"
        result = await self.session.execute(
            query,
            {"search_term": search_pattern, "skip": skip, "limit": limit}
        )
        rows = result.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    async def count_search(self, search_term: str) -> int:
        """Cuenta resultados de búsqueda usando SQL RAW"""
        query = text("""
            SELECT COUNT(id) as total
            FROM puntos_flesan.beneficios
            WHERE 
                LOWER(beneficio) LIKE LOWER(:search_term)
                OR LOWER(detalle) LIKE LOWER(:search_term)
                OR LOWER(regla1) LIKE LOWER(:search_term)
                OR LOWER(regla2) LIKE LOWER(:search_term)
        """)
        
        search_pattern = f"%{search_term}%"
        result = await self.session.execute(query, {"search_term": search_pattern})
        row = result.fetchone()
        return row.total if row else 0
    
    async def get_summary(self) -> dict:
        """Obtiene resumen de beneficios usando SQL RAW"""
        query = text("""
            SELECT 
                COUNT(*) as total_beneficios,
                COUNT(*) FILTER (WHERE is_active = true) as beneficios_activos,
                COALESCE(SUM(valor) FILTER (WHERE is_active = true), 0) as valor_total
            FROM puntos_flesan.beneficios
        """)
        
        result = await self.session.execute(query)
        row = result.fetchone()
        
        return {
            "total_beneficios": row.total_beneficios,
            "beneficios_activos": row.beneficios_activos,
            "valor_total": row.valor_total
        }
    
    def _row_to_dict(self, row) -> dict:
        """Convierte una fila de SQL RAW a diccionario"""
        if not row:
            return None
        
        return {
            "id": UUID(row.id) if isinstance(row.id, str) else row.id,
            "imagen": row.imagen,
            "beneficio": row.beneficio,
            "detalle": row.detalle,
            "regla1": row.regla1,
            "regla2": row.regla2,
            "valor": row.valor,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }
