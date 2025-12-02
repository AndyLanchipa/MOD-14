import pytest
from pydantic import ValidationError

from app.schemas.user_schemas import UserCreate, UserLogin


class TestUserCreateSchema:
    """Test UserCreate schema validation."""

    def test_valid_user_create(self):
        """Test creating a valid user."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
        }
        user = UserCreate(**user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "Password123!"

    def test_username_too_short(self):
        """Test username validation with too short username."""
        user_data = {
            "username": "ab",
            "email": "test@example.com",
            "password": "Password123!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Username must be at least 3 characters long" in str(exc_info.value)

    def test_username_too_long(self):
        """Test username validation with too long username."""
        user_data = {
            "username": "a" * 51,
            "email": "test@example.com",
            "password": "Password123!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Username must be less than 50 characters long" in str(exc_info.value)

    def test_username_invalid_characters(self):
        """Test username validation with invalid characters."""
        user_data = {
            "username": "test@user",
            "email": "test@example.com",
            "password": "Password123!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Username can only contain letters, numbers, and underscores" in str(
            exc_info.value
        )

    def test_password_too_short(self):
        """Test password validation with too short password."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Pass1!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Password must be at least 8 characters long" in str(exc_info.value)

    def test_password_missing_uppercase(self):
        """Test password validation without uppercase letter."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Password must contain at least one uppercase letter" in str(
            exc_info.value
        )

    def test_password_missing_lowercase(self):
        """Test password validation without lowercase letter."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "PASSWORD123!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Password must contain at least one lowercase letter" in str(
            exc_info.value
        )

    def test_password_missing_digit(self):
        """Test password validation without digit."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password!",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Password must contain at least one digit" in str(exc_info.value)

    def test_invalid_email_format(self):
        """Test email validation with invalid format."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "Password123!",
        }

        with pytest.raises(ValidationError):
            UserCreate(**user_data)


class TestUserLoginSchema:
    """Test UserLogin schema."""

    def test_valid_user_login(self):
        """Test creating a valid login request."""
        login_data = {"username": "testuser", "password": "Password123!"}
        login = UserLogin(**login_data)

        assert login.username == "testuser"
        assert login.password == "Password123!"
