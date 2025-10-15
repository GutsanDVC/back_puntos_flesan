"""Cliente JWKS para validación de tokens JWT"""

import json
from typing import Dict, Optional
from urllib.parse import urljoin

import httpx
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logger import get_logger

logger = get_logger(__name__)


class JWKSClient:
    """Cliente para obtener y cachear claves JWKS"""
    
    def __init__(self):
        self._jwks_cache: Optional[Dict] = None
        self._client = httpx.AsyncClient(timeout=10.0)
    
    async def get_jwks(self) -> Dict:
        """Obtiene las claves JWKS del servidor de autenticación"""
        if self._jwks_cache is None:
            try:
                response = await self._client.get(settings.AUTH_JWKS_URL)
                response.raise_for_status()
                self._jwks_cache = response.json()
                logger.info("JWKS obtenidas exitosamente")
            except httpx.RequestError as e:
                logger.error(f"Error obteniendo JWKS: {e}")
                raise AuthenticationError(
                    "Error conectando con servidor de autenticación",
                    details={"error": str(e)}
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP obteniendo JWKS: {e.response.status_code}")
                raise AuthenticationError(
                    "Error obteniendo claves de autenticación",
                    details={"status_code": e.response.status_code}
                )
        
        return self._jwks_cache
    
    async def get_signing_key(self, kid: str) -> str:
        """Obtiene la clave de firma para un kid específico"""
        jwks = await self.get_jwks()
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return json.dumps(key)
        
        raise AuthenticationError(
            f"Clave de firma no encontrada para kid: {kid}",
            details={"kid": kid}
        )
    
    def clear_cache(self):
        """Limpia el cache de JWKS"""
        self._jwks_cache = None
        logger.info("Cache JWKS limpiado")
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self._client.aclose()


class JWTValidator:
    """Validador de tokens JWT"""
    
    def __init__(self):
        self.jwks_client = JWKSClient()
    
    async def validate_token(self, token: str) -> Dict:
        """Valida un token JWT y retorna los claims"""
        try:
            # Decodificar header para obtener kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise AuthenticationError("Token sin kid en header")
            
            # Obtener clave de firma
            signing_key = await self.jwks_client.get_signing_key(kid)
            
            # Validar token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=settings.AUTH_AUDIENCE,
                issuer=settings.AUTH_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                }
            )
            
            logger.info(f"Token validado exitosamente para usuario: {payload.get('sub')}")
            return payload
            
        except JWTError as e:
            logger.warning(f"Error validando JWT: {e}")
            raise AuthenticationError(
                "Token inválido",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Error inesperado validando token: {e}")
            raise AuthenticationError(
                "Error validando token",
                details={"error": str(e)}
            )
    
    async def introspect_token(self, token: str) -> Dict:
        """Introspección de token con servidor de autenticación"""
        try:
            introspect_url = urljoin(settings.AUTH_JWKS_URL.replace("/.well-known/jwks.json", ""), "/oauth/introspect")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    introspect_url,
                    data={"token": token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                introspection_result = response.json()
                
                if not introspection_result.get("active", False):
                    raise AuthenticationError("Token inactivo")
                
                logger.info(f"Token introspectado exitosamente para usuario: {introspection_result.get('sub')}")
                return introspection_result
                
        except httpx.RequestError as e:
            logger.error(f"Error en introspección de token: {e}")
            raise AuthenticationError(
                "Error conectando con servidor de autenticación",
                details={"error": str(e)}
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en introspección: {e.response.status_code}")
            raise AuthenticationError(
                "Error validando token con servidor",
                details={"status_code": e.response.status_code}
            )
    
    async def close(self):
        """Cierra recursos"""
        await self.jwks_client.close()


# Instancia global del validador
jwt_validator = JWTValidator()
