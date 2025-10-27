from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Annotated
from pydantic import field_validator, Field


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    

    # --------------------------------------------------
    # Ambiente
    # --------------------------------------------------
    ENVIRONMENT: str = "development"
    
    # --------------------------------------------------
    # Base de datos
    # --------------------------------------------------
    
    #default
    DB_HOST: str = Field(..., description="Host de la base de datos")
    DB_PORT: int = Field(5432, description="Puerto de conexión a la base de datos")
    DB_NAME: str = Field(..., description="Nombre de la base de datos")
    DB_USER: str = Field(..., description="Usuario de la base de datos")
    DB_PASSWORD: str = Field(..., description="Contraseña de la base de datos")
    DB_DRIVER: str = Field("asyncpg", description="Driver de conexión (asyncpg o psycopg2)")
    DB_ESQUEMA: str = Field('public', description="Esquema de la base de datos")
    
    #Datawarehouse
    DB_HOST_DW: str = Field(..., description="Host de la base de datos")
    DB_PORT_DW: int = Field(5432, description="Puerto de conexión a la base de datos")
    DB_NAME_DW: str = Field(..., description="Nombre de la base de datos")
    DB_USER_DW: str = Field(..., description="Usuario de la base de datos")
    DB_PASSWORD_DW: str = Field(..., description="Contraseña de la base de datos")
    DB_DRIVER_DW: str = Field("asyncpg", description="Driver de conexión (asyncpg o psycopg2)")

    @property
    def DATABASE_URL(self) -> str:
        """Construye automáticamente la URL de conexión"""
        return f"postgresql+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_DW(self) -> str:
        """Construye automáticamente la URL de conexión"""
        return f"postgresql+{self.DB_DRIVER_DW}://{self.DB_USER_DW}:{self.DB_PASSWORD_DW}@{self.DB_HOST_DW}:{self.DB_PORT_DW}/{self.DB_NAME_DW}"

    
    # --------------------------------------------------
    # Autenticación
    # --------------------------------------------------
    AUTH_JWKS_URL: str
    AUTH_AUDIENCE: str
    AUTH_ISSUER: str
    ALGORITHM: str = "HS256"
    
    # --------------------------------------------------
    # Cookies
    # --------------------------------------------------
    COOKIE_NAME: str = "session"
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "Lax"
    
    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    LOG_LEVEL: str = "INFO"
    
    CORS_ALLOWED_ORIGINS: Union[str, List[str]] = ""

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    def split_cors(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    # --------------------------------------------------
    # API
    # --------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Backend Template"
    VERSION: str = "1.0.0"
    
    # Seguridad
    SECRET_KEY: str
    
    # Configuración del servidor
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8001
    WORKERS: int = 4
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignorar variables extra del entorno
    )


settings = Settings()
