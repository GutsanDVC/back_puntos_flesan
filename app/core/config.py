from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # Base de datos
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"
    
    # Autenticación
    AUTH_JWKS_URL: str
    AUTH_AUDIENCE: str
    AUTH_ISSUER: str
    
    # Cookies
    COOKIE_NAME: str = "session"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "Lax"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = []
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Backend Template"
    VERSION: str = "1.0.0"
    
    # Seguridad
    SECRET_KEY: str
    
    # Configuración del servidor
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8001
    WORKERS: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
