"""Tests end-to-end para endpoints de usuarios"""

from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.core.security import Role


class TestUserEndpoints:
    """Tests E2E para endpoints de usuarios"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test endpoint de health check"""
        response = await client.get("/health/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "database" in data
    
    @pytest.mark.asyncio
    async def test_create_user_without_auth_returns_401(self, client: AsyncClient):
        """Test crear usuario sin autenticación retorna 401"""
        user_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "roles": ["user"]
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.auth.dependencies.get_current_user')
    async def test_create_user_with_admin_auth_success(
        self, 
        mock_get_current_user,
        client: AsyncClient,
        mock_current_user
    ):
        """Test crear usuario con autenticación de admin"""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        user_data = {
            "email": "test@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
            "roles": ["user"]
        }
        
        # Mock de dependencias
        with patch('app.interfaces.api.dependencies.get_user_repository') as mock_repo, \
             patch('app.interfaces.api.dependencies.get_email_service') as mock_email, \
             patch('app.interfaces.api.dependencies.get_audit_service') as mock_audit:
            
            # Configurar mocks
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.exists_by_email.return_value = False
            mock_repo_instance.create.return_value = Mock(
                id=uuid4(),
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                full_name=f"{user_data['first_name']} {user_data['last_name']}",
                roles=[Role.USER],
                is_active=True,
                created_at=Mock(),
                updated_at=None,
                last_login=None
            )
            
            # Act
            response = await client.post("/api/v1/users/", json=user_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert data["roles"] == ["user"]
        assert data["is_active"] is True
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.auth.dependencies.get_current_user')
    async def test_get_user_by_id_success(
        self,
        mock_get_current_user,
        client: AsyncClient,
        mock_current_user
    ):
        """Test obtener usuario por ID"""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        user_id = uuid4()
        
        with patch('app.interfaces.api.dependencies.get_user_repository') as mock_repo:
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.get_by_id.return_value = Mock(
                id=user_id,
                email="test@example.com",
                first_name="Juan",
                last_name="Pérez",
                full_name="Juan Pérez",
                roles=[Role.USER],
                is_active=True,
                created_at=Mock(),
                updated_at=None,
                last_login=None
            )
            
            # Act
            response = await client.get(f"/api/v1/users/{user_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Juan"
        assert data["last_name"] == "Pérez"
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.auth.dependencies.get_current_user')
    async def test_get_nonexistent_user_returns_404(
        self,
        mock_get_current_user,
        client: AsyncClient,
        mock_current_user
    ):
        """Test obtener usuario inexistente retorna 404"""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        user_id = uuid4()
        
        with patch('app.interfaces.api.dependencies.get_user_repository') as mock_repo:
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.get_by_id.return_value = None
            
            # Act
            response = await client.get(f"/api/v1/users/{user_id}")
        
        # Assert
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.auth.dependencies.get_current_user')
    async def test_list_users_success(
        self,
        mock_get_current_user,
        client: AsyncClient,
        mock_current_user
    ):
        """Test listar usuarios"""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        
        with patch('app.interfaces.api.dependencies.get_user_repository') as mock_repo:
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.list_users.return_value = [
                Mock(
                    id=uuid4(),
                    email="user1@example.com",
                    first_name="User1",
                    last_name="Test",
                    full_name="User1 Test",
                    roles=[Role.USER],
                    is_active=True,
                    created_at=Mock(),
                    updated_at=None,
                    last_login=None
                ),
                Mock(
                    id=uuid4(),
                    email="user2@example.com",
                    first_name="User2",
                    last_name="Test",
                    full_name="User2 Test",
                    roles=[Role.USER],
                    is_active=True,
                    created_at=Mock(),
                    updated_at=None,
                    last_login=None
                )
            ]
            mock_repo_instance.count_users.return_value = 2
            
            # Act
            response = await client.get("/api/v1/users/?page=1&size=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 2
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["size"] == 10
    
    @pytest.mark.asyncio
    @patch('app.infrastructure.auth.dependencies.get_current_user')
    async def test_update_user_success(
        self,
        mock_get_current_user,
        client: AsyncClient,
        mock_current_user
    ):
        """Test actualizar usuario"""
        # Arrange
        mock_get_current_user.return_value = mock_current_user
        user_id = uuid4()
        
        update_data = {
            "first_name": "Juan Carlos",
            "last_name": "Pérez González"
        }
        
        with patch('app.interfaces.api.dependencies.get_user_repository') as mock_repo, \
             patch('app.interfaces.api.dependencies.get_audit_service') as mock_audit:
            
            mock_repo_instance = mock_repo.return_value
            mock_repo_instance.get_by_id.return_value = Mock(
                id=user_id,
                email="test@example.com",
                first_name="Juan",
                last_name="Pérez",
                roles=[Role.USER],
                is_active=True,
                created_at=Mock(),
                updated_at=None,
                last_login=None
            )
            mock_repo_instance.exists_by_email.return_value = False
            mock_repo_instance.update.return_value = Mock(
                id=user_id,
                email="test@example.com",
                first_name=update_data["first_name"],
                last_name=update_data["last_name"],
                full_name=f"{update_data['first_name']} {update_data['last_name']}",
                roles=[Role.USER],
                is_active=True,
                created_at=Mock(),
                updated_at=Mock(),
                last_login=None
            )
            
            # Act
            response = await client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]
    
    @pytest.mark.asyncio
    async def test_readiness_check(self, client: AsyncClient):
        """Test endpoint de readiness"""
        response = await client.get("/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_liveness_check(self, client: AsyncClient):
        """Test endpoint de liveness"""
        response = await client.get("/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data
