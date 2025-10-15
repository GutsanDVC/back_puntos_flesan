"""Gateway para servicio de auditoría externo"""

from datetime import datetime
from typing import Dict
from uuid import UUID

import httpx

from app.application.users.ports import AuditServicePort
from app.core.logger import get_logger
from app.domain.users.entities import User

logger = get_logger(__name__)


class AuditGateway(AuditServicePort):
    """Implementación del gateway de auditoría usando servicio externo"""
    
    def __init__(self, base_url: str = "https://api.auditservice.com", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def log_user_created(self, user: User, created_by: UUID) -> None:
        """Registra creación de usuario"""
        audit_data = {
            "event_type": "user_created",
            "resource_type": "user",
            "resource_id": str(user.id),
            "actor_id": str(created_by),
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "user_email": user.email,
                "user_roles": [role.value for role in user.roles],
                "user_name": user.full_name
            }
        }
        
        await self._send_audit_log(audit_data)
    
    async def log_user_updated(self, user: User, updated_by: UUID) -> None:
        """Registra actualización de usuario"""
        audit_data = {
            "event_type": "user_updated",
            "resource_type": "user",
            "resource_id": str(user.id),
            "actor_id": str(updated_by),
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "user_email": user.email,
                "user_roles": [role.value for role in user.roles],
                "user_name": user.full_name,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        }
        
        await self._send_audit_log(audit_data)
    
    async def log_user_deactivated(self, user: User, deactivated_by: UUID) -> None:
        """Registra desactivación de usuario"""
        audit_data = {
            "event_type": "user_deactivated",
            "resource_type": "user",
            "resource_id": str(user.id),
            "actor_id": str(deactivated_by),
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "user_email": user.email,
                "user_roles": [role.value for role in user.roles],
                "user_name": user.full_name,
                "is_active": user.is_active
            }
        }
        
        await self._send_audit_log(audit_data)
    
    async def log_role_assigned(self, user: User, role: str, assigned_by: UUID) -> None:
        """Registra asignación de rol"""
        audit_data = {
            "event_type": "role_assigned",
            "resource_type": "user",
            "resource_id": str(user.id),
            "actor_id": str(assigned_by),
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "user_email": user.email,
                "assigned_role": role,
                "current_roles": [r.value for r in user.roles],
                "user_name": user.full_name
            }
        }
        
        await self._send_audit_log(audit_data)
    
    async def _send_audit_log(self, audit_data: Dict) -> None:
        """Método privado para enviar log de auditoría"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.base_url}/audit-logs",
                json=audit_data,
                headers=headers
            )
            
            response.raise_for_status()
            logger.info(f"Log de auditoría enviado: {audit_data['event_type']}")
            
        except httpx.RequestError as e:
            logger.error(f"Error de conexión enviando audit log: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP enviando audit log: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error inesperado enviando audit log: {e}")
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()


class MockAuditGateway(AuditServicePort):
    """Implementación mock del gateway de auditoría para desarrollo/testing"""
    
    async def log_user_created(self, user: User, created_by: UUID) -> None:
        """Mock: simula registro de creación de usuario"""
        logger.info(f"[MOCK AUDIT] Usuario creado: {user.email} por {created_by}")
    
    async def log_user_updated(self, user: User, updated_by: UUID) -> None:
        """Mock: simula registro de actualización de usuario"""
        logger.info(f"[MOCK AUDIT] Usuario actualizado: {user.email} por {updated_by}")
    
    async def log_user_deactivated(self, user: User, deactivated_by: UUID) -> None:
        """Mock: simula registro de desactivación de usuario"""
        logger.info(f"[MOCK AUDIT] Usuario desactivado: {user.email} por {deactivated_by}")
    
    async def log_role_assigned(self, user: User, role: str, assigned_by: UUID) -> None:
        """Mock: simula registro de asignación de rol"""
        logger.info(f"[MOCK AUDIT] Rol {role} asignado a {user.email} por {assigned_by}")
