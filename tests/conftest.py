"""Configuración global para tests con pytest"""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infrastructure.db.session import Base
from app.main import app


# Configurar event loop para tests async
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Crea un event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Base de datos de test
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture para sesión de base de datos de test"""
    
    # Crear tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear sesión
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Limpiar tablas después del test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture para cliente HTTP de test"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_current_user():
    """Fixture para usuario mock"""
    from app.core.security import CurrentUser, Role, Permission
    
    return CurrentUser(
        user_id=str(uuid4()),
        email="test@example.com",
        roles=[Role.ADMIN],
        permissions={Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN},
        is_active=True
    )


@pytest.fixture
def mock_regular_user():
    """Fixture para usuario regular mock"""
    from app.core.security import CurrentUser, Role, Permission
    
    return CurrentUser(
        user_id=str(uuid4()),
        email="user@example.com",
        roles=[Role.USER],
        permissions={Permission.READ, Permission.WRITE},
        is_active=True
    )


# Override de dependencias para tests
def override_get_db():
    """Override para la dependencia de base de datos"""
    return db_session


# Configurar overrides
app.dependency_overrides = {}
