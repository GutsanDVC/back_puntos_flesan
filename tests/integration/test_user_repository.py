"""Tests de integración para UserRepository"""

from datetime import datetime
from uuid import uuid4

import pytest

from app.core.security import Role
from app.domain.users.entities import User
from app.infrastructure.db.repositories import SQLAlchemyUserRepository


class TestSQLAlchemyUserRepository:
    """Tests de integración para SQLAlchemyUserRepository"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test crear usuario en base de datos"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Act
        created_user = await repository.create(user)
        
        # Assert
        assert created_user.id == user.id
        assert created_user.email == user.email
        assert created_user.first_name == user.first_name
        assert created_user.last_name == user.last_name
        assert created_user.roles == user.roles
        assert created_user.is_active == user.is_active
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_session):
        """Test obtener usuario por ID"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        await repository.create(user)
        
        # Act
        found_user = await repository.get_by_id(user.id)
        
        # Assert
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session):
        """Test obtener usuario por ID no encontrado"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        non_existent_id = uuid4()
        
        # Act
        found_user = await repository.get_by_id(non_existent_id)
        
        # Assert
        assert found_user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session):
        """Test obtener usuario por email"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        await repository.create(user)
        
        # Act
        found_user = await repository.get_by_email("test@example.com")
        
        # Assert
        assert found_user is not None
        assert found_user.email == user.email
        assert found_user.id == user.id
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session):
        """Test obtener usuario por email no encontrado"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        
        # Act
        found_user = await repository.get_by_email("nonexistent@example.com")
        
        # Assert
        assert found_user is None
    
    @pytest.mark.asyncio
    async def test_update_user(self, db_session):
        """Test actualizar usuario"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        created_user = await repository.create(user)
        
        # Modificar usuario
        created_user.first_name = "Juan Carlos"
        created_user.updated_at = datetime.utcnow()
        
        # Act
        updated_user = await repository.update(created_user)
        
        # Assert
        assert updated_user.first_name == "Juan Carlos"
        assert updated_user.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_exists_by_email(self, db_session):
        """Test verificar existencia por email"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        await repository.create(user)
        
        # Act & Assert
        assert await repository.exists_by_email("test@example.com") is True
        assert await repository.exists_by_email("nonexistent@example.com") is False
    
    @pytest.mark.asyncio
    async def test_list_users(self, db_session):
        """Test listar usuarios"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        
        # Crear varios usuarios
        users = []
        for i in range(5):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                last_name="Test",
                roles=[Role.USER],
                is_active=True,
                created_at=datetime.utcnow()
            )
            users.append(await repository.create(user))
        
        # Act
        listed_users = await repository.list_users(skip=0, limit=10)
        
        # Assert
        assert len(listed_users) == 5
        assert all(user.email.startswith("user") for user in listed_users)
    
    @pytest.mark.asyncio
    async def test_list_users_with_pagination(self, db_session):
        """Test listar usuarios con paginación"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        
        # Crear varios usuarios
        for i in range(5):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                last_name="Test",
                roles=[Role.USER],
                is_active=True,
                created_at=datetime.utcnow()
            )
            await repository.create(user)
        
        # Act
        first_page = await repository.list_users(skip=0, limit=2)
        second_page = await repository.list_users(skip=2, limit=2)
        
        # Assert
        assert len(first_page) == 2
        assert len(second_page) == 2
        assert first_page[0].id != second_page[0].id
    
    @pytest.mark.asyncio
    async def test_count_users(self, db_session):
        """Test contar usuarios"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        
        # Crear varios usuarios
        for i in range(3):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                last_name="Test",
                roles=[Role.USER],
                is_active=True,
                created_at=datetime.utcnow()
            )
            await repository.create(user)
        
        # Act
        count = await repository.count_users()
        
        # Assert
        assert count == 3
    
    @pytest.mark.asyncio
    async def test_delete_user_soft_delete(self, db_session):
        """Test eliminar usuario (soft delete)"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        created_user = await repository.create(user)
        
        # Act
        deleted = await repository.delete(created_user.id)
        
        # Assert
        assert deleted is True
        
        # Verificar que el usuario sigue existiendo pero inactivo
        found_user = await repository.get_by_id(created_user.id)
        assert found_user is not None
        assert found_user.is_active is False
