"""Repositorio de usuarios - Acceso a datos con SQL RAW"""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import Role


class UserRepository:
    """Repositorio para operaciones de base de datos de usuarios usando SQL RAW"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        user_id:int,
        email: str,
        first_name: str,
        last_name: str,
        roles: List[Role],
        puntos: int = 0
    ) -> dict:
        """Crea un nuevo usuario usando SQL RAW"""
        id = uuid4()
        roles_json = json.dumps([role.value for role in roles])
        created_at = datetime.utcnow()
        
        query = text("""
            INSERT INTO puntos_flesan.users 
            (id,user_id, email, first_name, last_name, puntos_disponibles, rol, permisos, 
             is_active, created_at, updated_at, last_login)
            VALUES 
            (:id, :user_id, :email, :first_name, :last_name, :puntos, :rol, :permisos,
             :is_active, :created_at, :updated_at, :last_login)
            RETURNING id, user_id, email, first_name, last_name, puntos_disponibles, rol, permisos,
                      is_active, created_at, updated_at, last_login
        """)
        
        result = await self.session.execute(
            query,
            {
                "id": str(id),
                "user_id": str(user_id),
                "email": email.lower(),
                "first_name": first_name,
                "last_name": last_name,
                "puntos": puntos,
                "rol": roles[0].value if roles else "USER",
                "permisos": roles_json,
                "is_active": True,
                "created_at": created_at,
                "updated_at": None,
                "last_login": None
            }
        )
        
        row = result.fetchone()
        return self._row_to_dict(row)
    
    async def get_by_id(self, user_id: int) -> Optional[dict]:
        """Obtiene un usuario por ID usando SQL RAW"""
        query = text("""
            SELECT id, user_id, email, first_name, last_name, puntos_disponibles, rol, permisos,
                   is_active, created_at, updated_at, last_login
            FROM puntos_flesan.users
            WHERE user_id = :user_id
        """)
        
        result = await self.session.execute(query, {"user_id": int(user_id)})
        row = result.fetchone()
        return self._row_to_dict(row) if row else None
    
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por email usando SQL RAW"""
        query = text("""
            SELECT id, user_id, email, first_name, last_name, puntos_disponibles, rol, permisos,
                   is_active, created_at, updated_at, last_login
            FROM puntos_flesan.users
            WHERE email = :email
        """)
        
        result = await self.session.execute(query, {"email": email.lower()})
        row = result.fetchone()
        
        return self._row_to_dict(row) if row else None
    
    async def get_by_user_id(self, user_id: int) -> Optional[dict]:
        """Obtiene un usuario por user_id (ID del datawarehouse) usando SQL RAW"""
        query = text("""
            SELECT id, user_id, email, first_name, last_name, puntos_disponibles, rol, permisos,
                   is_active, created_at, updated_at, last_login
            FROM puntos_flesan.users
            WHERE user_id = :user_id
        """)
        
        result = await self.session.execute(query, {"user_id": user_id})
        row = result.fetchone()
        
        return self._row_to_dict(row) if row else None
    
    async def update(
        self,
        user_id: int,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        roles: Optional[List[Role]] = None,
        puntos: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> dict:
        """Actualiza un usuario usando SQL RAW"""
        # Obtener usuario actual
        user = await self.get_by_id(user_id)
        print(user)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        
        # Preparar valores actualizados
        updated_email = email.lower() if email else user["email"]
        updated_first_name = first_name if first_name else user["first_name"]
        updated_last_name = last_name if last_name else user["last_name"]
        updated_puntos = puntos if puntos is not None else user["puntos"]
        updated_is_active = is_active if is_active is not None else user["is_active"]
        
        # if roles:
        #     updated_roles_json = json.dumps([role.value for role in roles])
        #     updated_rol = roles[0].value
        # else:
        #     updated_roles_json = user["permisos"]
        #     updated_rol = user["rol"]
        
        query = text("""
            UPDATE puntos_flesan.users
            SET email = :email,
                first_name = :first_name,
                last_name = :last_name,
                puntos_disponibles = :puntos,
                is_active = :is_active,
                updated_at = :updated_at
            WHERE user_id = :user_id
            RETURNING id, user_id, email, first_name, last_name, puntos_disponibles, rol, permisos,
                      is_active, created_at, updated_at, last_login
        """)
        
        result = await self.session.execute(
            query,
            {
                "user_id": user_id,
                "email": updated_email,
                "first_name": updated_first_name,
                "last_name": updated_last_name,
                "puntos": updated_puntos,
                "is_active": updated_is_active,
                "updated_at": datetime.utcnow()
            }
        )
        
        row = result.fetchone()
        return self._row_to_dict(row)
    
    async def delete(self, user_id: int) -> bool:
        """Elimina un usuario (soft delete) usando SQL RAW"""
        query = text("""
            UPDATE puntos_flesan.users
            SET is_active = false,
                updated_at = :updated_at
            WHERE id = :user_id
            RETURNING id
        """)
        
        result = await self.session.execute(
            query,
            {
                "user_id": user_id,
                "updated_at": datetime.utcnow()
            }
        )
        
        row = result.fetchone()
        return row is not None
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[dict]:
        """Lista usuarios con filtros usando SQL RAW"""
        where_conditions = []
        params = {"skip": skip, "limit": limit}
        
        if email:
            where_conditions.append("email ILIKE :email")
            params["email"] = f"%{email}%"
        
        if is_active is not None:
            where_conditions.append("is_active = :is_active")
            params["is_active"] = is_active
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT id, user_id, email, first_name, last_name, puntos_disponibles, rol, permisos,
                   is_active, created_at, updated_at, last_login
            FROM puntos_flesan.users
            {where_clause}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
        """)
        
        result = await self.session.execute(query, params)
        rows = result.fetchall()
        
        return [self._row_to_dict(row) for row in rows]
    
    async def count_users(
        self,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Cuenta usuarios con filtros usando SQL RAW"""
        where_conditions = []
        params = {}
        
        if email:
            where_conditions.append("email ILIKE :email")
            params["email"] = f"%{email}%"
        
        if is_active is not None:
            where_conditions.append("is_active = :is_active")
            params["is_active"] = is_active
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = text(f"""
            SELECT COUNT(id) as total
            FROM puntos_flesan.users
            {where_clause}
        """)
        
        result = await self.session.execute(query, params)
        row = result.fetchone()
        return row.total if row else 0
    
    async def exists_by_email(self, email: str) -> bool:
        """Verifica si existe un usuario con el email dado usando SQL RAW"""
        query = text("""
            SELECT COUNT(id) as total
            FROM puntos_flesan.users
            WHERE email = :email
        """)
        
        result = await self.session.execute(query, {"email": email.lower()})
        row = result.fetchone()
        count = row.total if row else 0
        return count > 0
    
    def _row_to_dict(self, row) -> dict:
        """Convierte una fila de SQL RAW a diccionario"""
        if not row:
            return None
        permissions = [row.permisos if hasattr(row, "permisos") else row_dict.get("permisos")]
        return {
            "id": UUID(row.id) if isinstance(row.id, str) else row.id,
            "user_id": row.user_id if hasattr(row, 'user_id') else None,
            "email": row.email,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "full_name": f"{row.first_name} {row.last_name}",
            "role": row.rol,
            "permissions": permissions,
            "puntos": row.puntos_disponibles,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "last_login": row.last_login
        }
