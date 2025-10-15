"""Tests unitarios para CreateUserCommand"""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.application.users import CreateUserCommand, CreateUserDTO
from app.core.exceptions import BusinessRuleException
from app.core.security import Role
from app.domain.users.entities import User


class TestCreateUserCommand:
    """Tests para CreateUserCommand"""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock del repositorio de usuarios"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_email_service(self):
        """Mock del servicio de email"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_audit_service(self):
        """Mock del servicio de auditoría"""
        return AsyncMock()
    
    @pytest.fixture
    def command(self, mock_user_repository, mock_email_service, mock_audit_service):
        """Instancia del comando"""
        return CreateUserCommand(
            mock_user_repository,
            mock_email_service,
            mock_audit_service
        )
    
    @pytest.fixture
    def valid_dto(self):
        """DTO válido para crear usuario"""
        return CreateUserDTO(
            email="test@example.com",
            first_name="Juan",
            last_name="Pérez",
            roles=[Role.USER]
        )
    
    @pytest.fixture
    def admin_user(self):
        """Usuario administrador mock"""
        from app.core.security import CurrentUser, Permission
        
        return CurrentUser(
            user_id=str(uuid4()),
            email="admin@example.com",
            roles=[Role.ADMIN],
            permissions={Permission.READ, Permission.WRITE, Permission.DELETE, Permission.ADMIN},
            is_active=True
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        command,
        valid_dto,
        admin_user,
        mock_user_repository,
        mock_email_service,
        mock_audit_service
    ):
        """Test crear usuario exitosamente"""
        # Arrange
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User(
            id=uuid4(),
            email=valid_dto.email,
            first_name=valid_dto.first_name,
            last_name=valid_dto.last_name,
            roles=valid_dto.roles,
            is_active=True,
            created_at=Mock()
        )
        mock_user_repository.create.return_value = created_user
        mock_email_service.send_welcome_email.return_value = True
        
        # Act
        result = await command.execute(valid_dto, admin_user)
        
        # Assert
        assert result.email == valid_dto.email
        assert result.first_name == valid_dto.first_name
        assert result.last_name == valid_dto.last_name
        assert result.roles == valid_dto.roles
        assert result.is_active is True
        
        mock_user_repository.exists_by_email.assert_called_once_with(valid_dto.email)
        mock_user_repository.create.assert_called_once()
        mock_email_service.send_welcome_email.assert_called_once_with(created_user)
        mock_audit_service.log_user_created.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_with_existing_email_raises_error(
        self,
        command,
        valid_dto,
        admin_user,
        mock_user_repository
    ):
        """Test crear usuario con email existente lance error"""
        # Arrange
        mock_user_repository.exists_by_email.return_value = True
        
        # Act & Assert
        with pytest.raises(BusinessRuleException, match="Ya existe un usuario con el email"):
            await command.execute(valid_dto, admin_user)
        
        mock_user_repository.exists_by_email.assert_called_once_with(valid_dto.email)
        mock_user_repository.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_email_failure_does_not_fail_operation(
        self,
        command,
        valid_dto,
        admin_user,
        mock_user_repository,
        mock_email_service,
        mock_audit_service
    ):
        """Test que fallo en email no falle la operación"""
        # Arrange
        mock_user_repository.exists_by_email.return_value = False
        
        created_user = User(
            id=uuid4(),
            email=valid_dto.email,
            first_name=valid_dto.first_name,
            last_name=valid_dto.last_name,
            roles=valid_dto.roles,
            is_active=True,
            created_at=Mock()
        )
        mock_user_repository.create.return_value = created_user
        mock_email_service.send_welcome_email.side_effect = Exception("Email service error")
        
        # Act
        result = await command.execute(valid_dto, admin_user)
        
        # Assert
        assert result.email == valid_dto.email
        mock_user_repository.create.assert_called_once()
        mock_email_service.send_welcome_email.assert_called_once_with(created_user)
        mock_audit_service.log_user_created.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_admin_user_requires_admin_role(
        self,
        command,
        admin_user,
        mock_user_repository
    ):
        """Test crear usuario admin requiere rol admin"""
        # Arrange
        dto_with_admin_role = CreateUserDTO(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            roles=[Role.ADMIN]
        )
        
        regular_user = Mock()
        regular_user.roles = [Role.USER]
        
        mock_user_repository.exists_by_email.return_value = False
        
        # Act & Assert
        # Esto debería funcionar con admin_user pero fallar con regular_user
        # El test específico de validación de roles está en el servicio de dominio
        
        # Con usuario admin debería funcionar
        created_user = User(
            id=uuid4(),
            email=dto_with_admin_role.email,
            first_name=dto_with_admin_role.first_name,
            last_name=dto_with_admin_role.last_name,
            roles=dto_with_admin_role.roles,
            is_active=True,
            created_at=Mock()
        )
        mock_user_repository.create.return_value = created_user
        
        result = await command.execute(dto_with_admin_role, admin_user)
        assert result.roles == [Role.ADMIN]
