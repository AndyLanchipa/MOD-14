import pytest
from sqlalchemy.orm import Session

from app.schemas.user_schemas import UserCreate
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)


class TestUserService:
    """Test CRUD operations for users."""

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation."""
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="Password123!"
        )

        user = create_user(db_session, user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "Password123!"  # Should be hashed
        assert user.created_at is not None

    def test_create_user_duplicate_username(self, db_session: Session):
        """Test user creation with duplicate username."""
        user_data1 = UserCreate(
            username="testuser", email="test1@example.com", password="Password123!"
        )
        user_data2 = UserCreate(
            username="testuser", email="test2@example.com", password="Password123!"
        )

        create_user(db_session, user_data1)

        with pytest.raises(ValueError, match="Username already exists"):
            create_user(db_session, user_data2)

    def test_create_user_duplicate_email(self, db_session: Session):
        """Test user creation with duplicate email."""
        user_data1 = UserCreate(
            username="testuser1", email="test@example.com", password="Password123!"
        )
        user_data2 = UserCreate(
            username="testuser2", email="test@example.com", password="Password123!"
        )

        create_user(db_session, user_data1)

        with pytest.raises(ValueError, match="Email already exists"):
            create_user(db_session, user_data2)

    def test_get_user_by_username_exists(self, db_session: Session):
        """Test getting existing user by username."""
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="Password123!"
        )
        created_user = create_user(db_session, user_data)

        retrieved_user = get_user_by_username(db_session, "testuser")

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "testuser"

    def test_get_user_by_username_not_exists(self, db_session: Session):
        """Test getting non-existing user by username."""
        user = get_user_by_username(db_session, "nonexistent")
        assert user is None

    def test_get_user_by_email_exists(self, db_session: Session):
        """Test getting existing user by email."""
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="Password123!"
        )
        created_user = create_user(db_session, user_data)

        retrieved_user = get_user_by_email(db_session, "test@example.com")

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"

    def test_get_user_by_email_not_exists(self, db_session: Session):
        """Test getting non-existing user by email."""
        user = get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication."""
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="Password123!"
        )
        create_user(db_session, user_data)

        authenticated_user = authenticate_user(db_session, "testuser", "Password123!")

        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"

    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test user authentication with wrong password."""
        user_data = UserCreate(
            username="testuser", email="test@example.com", password="Password123!"
        )
        create_user(db_session, user_data)

        authenticated_user = authenticate_user(db_session, "testuser", "WrongPassword")

        assert authenticated_user is None

    def test_authenticate_user_not_exists(self, db_session: Session):
        """Test authentication for non-existing user."""
        authenticated_user = authenticate_user(
            db_session, "nonexistent", "Password123!"
        )
        assert authenticated_user is None
