"""Tests unitarios para la entidad User"""

from datetime import datetime
from uuid import uuid4

import pytest

from app.core.security import Role
from app.domain.users.entities import User


class TestUserEntity:
    """Tests para la entidad User"""
    
    def test_create_valid_user(self):
        """Test crear usuario válido"""
        user_id = uuid4()
        email = "test@example.com"
        first_name = "Juan"
        last_name = "Pérez"
        roles = [Role.USER]
        created_at = datetime.utcnow()
        
        user = User(
            id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            is_active=True,
            created_at=created_at
        )
        
        assert user.id == user_id
        assert user.email == email
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.roles == roles
        assert user.is_active is True
        assert user.created_at == created_at
        assert user.full_name == "Juan Pérez"
    
    def test_user_with_invalid_email_raises_error(self):
        """Test que email inválido lance error"""
        with pytest.raises(ValueError, match="Email inválido"):
            User(
                id=uuid4(),
                email="invalid-email",
                first_name="Juan",
                last_name="Pérez",
                roles=[Role.USER],
                is_active=True,
                created_at=datetime.utcnow()
            )
    
    def test_user_with_empty_first_name_raises_error(self):
        """Test que nombre vacío lance error"""
        with pytest.raises(ValueError, match="Nombre es requerido"):
            User(
                id=uuid4(),
                email="test@example.com",
                first_name="",
                last_name="Pérez",
                roles=[Role.USER],
                is_active=True,
                created_at=datetime.utcnow()
            )
    
    def test_user_with_empty_last_name_raises_error(self):
        """Test que apellido vacío lance error"""
        with pytest.raises(ValueError, match="Apellido es requerido"):
            User(
                id=uuid4(),
                email="test@example.com",
                first_name="Juan",
                last_name="",
                roles=[Role.USER],
                is_active=True,
                created_at=datetime.utcnow()
            )
    
    def test_user_without_roles_raises_error(self):
        """Test que usuario sin roles lance error"""
        with pytest.raises(ValueError, match="Usuario debe tener al menos un rol"):
            User(
                id=uuid4(),
                email="test@example.com",
                first_name="Juan",
                last_name="Pérez",
                roles=[],
                is_active=True,
                created_at=datetime.utcnow()
            )
    
    def test_has_role(self):
        """Test verificar si usuario tiene rol"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER, Role.MANAGER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        assert user.has_role(Role.USER) is True
        assert user.has_role(Role.MANAGER) is True
        assert user.has_role(Role.ADMIN) is False
    
    def test_add_role(self):
        """Test agregar rol a usuario"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        user.add_role(Role.MANAGER)
        
        assert Role.MANAGER in user.roles
        assert len(user.roles) == 2
    
    def test_add_existing_role_does_nothing(self):
        """Test agregar rol existente no hace nada"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        user.add_role(Role.USER)
        
        assert len(user.roles) == 1
        assert user.roles[0] == Role.USER
    
    def test_remove_role(self):
        """Test remover rol de usuario"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER, Role.MANAGER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        user.remove_role(Role.MANAGER)
        
        assert Role.MANAGER not in user.roles
        assert len(user.roles) == 1
        assert user.roles[0] == Role.USER
    
    def test_activate_user(self):
        """Test activar usuario"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=False,
            created_at=datetime.utcnow()
        )
        
        user.activate()
        
        assert user.is_active is True
    
    def test_deactivate_user(self):
        """Test desactivar usuario"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        user.deactivate()
        
        assert user.is_active is False
    
    def test_update_last_login(self):
        """Test actualizar último login"""
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        login_time = datetime.utcnow()
        user.update_last_login(login_time)
        
        assert user.last_login == login_time
