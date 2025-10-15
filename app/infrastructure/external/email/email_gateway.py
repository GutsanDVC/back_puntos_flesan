"""Gateway para servicio de email externo"""

from typing import Dict, Optional

import httpx

from app.application.users.ports import EmailServicePort
from app.core.config import settings
from app.core.logger import get_logger
from app.domain.users.entities import User

logger = get_logger(__name__)


class EmailGateway(EmailServicePort):
    """Implementación del gateway de email usando servicio externo"""
    
    def __init__(self, base_url: str = "https://api.emailservice.com", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def send_welcome_email(self, user: User) -> bool:
        """Envía email de bienvenida"""
        try:
            email_data = {
                "to": user.email,
                "template": "welcome",
                "variables": {
                    "first_name": user.first_name,
                    "full_name": user.full_name,
                    "email": user.email
                }
            }
            
            response = await self._send_email(email_data)
            
            if response:
                logger.info(f"Email de bienvenida enviado a {user.email}")
                return True
            else:
                logger.error(f"Error enviando email de bienvenida a {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción enviando email de bienvenida: {e}")
            return False
    
    async def send_user_deactivated_email(self, user: User) -> bool:
        """Envía email de desactivación"""
        try:
            email_data = {
                "to": user.email,
                "template": "user_deactivated",
                "variables": {
                    "first_name": user.first_name,
                    "full_name": user.full_name,
                    "email": user.email
                }
            }
            
            response = await self._send_email(email_data)
            
            if response:
                logger.info(f"Email de desactivación enviado a {user.email}")
                return True
            else:
                logger.error(f"Error enviando email de desactivación a {user.email}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción enviando email de desactivación: {e}")
            return False
    
    async def _send_email(self, email_data: Dict) -> bool:
        """Método privado para enviar email al servicio externo"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.base_url}/send",
                json=email_data,
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result.get("success", False)
            
        except httpx.RequestError as e:
            logger.error(f"Error de conexión enviando email: {e}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP enviando email: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado enviando email: {e}")
            return False
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()


class MockEmailGateway(EmailServicePort):
    """Implementación mock del gateway de email para desarrollo/testing"""
    
    async def send_welcome_email(self, user: User) -> bool:
        """Mock: simula envío de email de bienvenida"""
        logger.info(f"[MOCK] Email de bienvenida enviado a {user.email}")
        return True
    
    async def send_user_deactivated_email(self, user: User) -> bool:
        """Mock: simula envío de email de desactivación"""
        logger.info(f"[MOCK] Email de desactivación enviado a {user.email}")
        return True
