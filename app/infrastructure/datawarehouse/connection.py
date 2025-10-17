"""Gestión de conexiones al datawarehouse - Solo lectura usando configuración existente"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.core.config import settings
from .exceptions import ConnectionError, TimeoutError


class DatawarehouseConnection:
    """Gestor de conexiones al datawarehouse (solo lectura)"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inicializa el engine de conexión usando configuración existente"""
        try:
            if not settings.DATABASE_URL_DW:
                raise ConnectionError("DATABASE_URL_DW no configurada")
            
            # Engine configurado para solo lectura usando configuración existente
            self.engine = create_async_engine(
                settings.DATABASE_URL_DW,
                echo=False,  # No mostrar SQL en logs por seguridad
                pool_timeout=30,  # Timeout por defecto
                pool_recycle=3600,  # Reciclar conexiones cada hora
                pool_pre_ping=True,  # Verificar conexiones antes de usar
                # Configuraciones de solo lectura
                connect_args={
                    "command_timeout": 60,  # Timeout de query por defecto
                    "server_settings": {
                        "application_name": "puntos_flesan_readonly"
                    }
                }
            )
        except Exception as e:
            raise ConnectionError(f"Error inicializando engine: {str(e)}")
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Obtiene una sesión de solo lectura"""
        if not self.session_factory:
            raise ConnectionError("Engine no inicializado")
        
        async with self.session_factory() as session:
            try:
                # Verificar que la conexión esté activa
                await asyncio.wait_for(
                    session.execute(text("SELECT 1")),
                    timeout=30  # Timeout por defecto
                )
                
                # Configurar sesión como solo lectura
                await session.execute(text("SET TRANSACTION READ ONLY"))
                
                yield session
                
            except asyncio.TimeoutError:
                raise TimeoutError("Timeout al conectar con datawarehouse")
            except Exception as e:
                raise ConnectionError(f"Error de conexión: {str(e)}")
    
    async def test_connection(self) -> tuple[bool, str]:
        """Prueba la conexión al datawarehouse"""
        try:
            async with self.get_session() as session:
                result = await session.execute(text("SELECT 1 as test"))
                success = result.scalar() == 1
                return success, "Conexión exitosa" if success else "Query falló"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    async def close(self):
        """Cierra las conexiones"""
        if self.engine:
            await self.engine.dispose()


# Instancia global del gestor de conexiones
try:
    dw_connection = DatawarehouseConnection()
except Exception as e:
    # Si falla la inicialización, crear una instancia que maneje el error
    print(f"Warning: Error inicializando DatawarehouseConnection: {e}")
    dw_connection = None
