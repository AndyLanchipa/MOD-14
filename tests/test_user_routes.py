import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from main import app


@pytest.fixture
def client(db_session):
    """Create a test client with database override"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123",
    }


@pytest.fixture
def registered_user(client, sample_user_data):
    """Create and return a registered user"""
    response = client.post("/api/users/register", json=sample_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_token(client, sample_user_data):
    """Get authentication token for a registered user"""
    # Register user first
    client.post("/api/users/register", json=sample_user_data)

    # Login to get token
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    response = client.post("/api/users/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]


class TestUserRegistration:
    """Tests for user registration endpoint"""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/users/register", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_username(self, client, sample_user_data):
        """Test registration with duplicate username"""
        # Register first user
        client.post("/api/users/register", json=sample_user_data)

        # Try to register with same username but different email
        duplicate_user = sample_user_data.copy()
        duplicate_user["email"] = "different@example.com"
        response = client.post("/api/users/register", json=duplicate_user)

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email"""
        # Register first user
        client.post("/api/users/register", json=sample_user_data)

        # Try to register with same email but different username
        duplicate_user = sample_user_data.copy()
        duplicate_user["username"] = "differentuser"
        response = client.post("/api/users/register", json=duplicate_user)

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_invalid_username(self, client, sample_user_data):
        """Test registration with invalid username"""
        invalid_user = sample_user_data.copy()
        invalid_user["username"] = "ab"  # Too short

        response = client.post("/api/users/register", json=invalid_user)
        assert response.status_code == 422

    def test_register_invalid_password(self, client, sample_user_data):
        """Test registration with invalid password"""
        invalid_user = sample_user_data.copy()
        invalid_user["password"] = "weak"  # Too short, no uppercase/number

        response = client.post("/api/users/register", json=invalid_user)
        assert response.status_code == 422

    def test_register_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email"""
        invalid_user = sample_user_data.copy()
        invalid_user["email"] = "not-an-email"

        response = client.post("/api/users/register", json=invalid_user)
        assert response.status_code == 422


class TestUserLogin:
    """Tests for user login endpoint"""

    def test_login_success(self, client, sample_user_data, registered_user):
        """Test successful user login"""
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        }
        response = client.post("/api/users/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client, sample_user_data, registered_user):
        """Test login with incorrect password"""
        login_data = {
            "username": sample_user_data["username"],
            "password": "WrongPassword123",
        }
        response = client.post("/api/users/login", data=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent username"""
        login_data = {"username": "nonexistent", "password": "SomePass123"}
        response = client.post("/api/users/login", data=login_data)

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials"""
        login_data = {"username": "", "password": ""}
        response = client.post("/api/users/login", data=login_data)

        # Empty credentials trigger validation errors (422) before auth logic
        assert response.status_code == 422


class TestGetCurrentUser:
    """Tests for getting current user information"""

    def test_get_current_user_success(self, client, auth_token, sample_user_data):
        """Test getting current user with valid token"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "password" not in data

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/users/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 401

    def test_get_current_user_expired_token(self, client, sample_user_data):
        """Test getting current user with malformed token"""
        # Use a clearly malformed token
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 401


class TestUserEndToEnd:
    """End-to-end tests for user workflow"""

    def test_complete_user_workflow(self, client):
        """Test complete user registration and login workflow"""
        # 1. Register a new user
        user_data = {
            "username": "completeuser",
            "email": "complete@example.com",
            "password": "CompletePass123",
        }
        register_response = client.post("/api/users/register", json=user_data)
        assert register_response.status_code == 201

        # 2. Login with the new user
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"],
        }
        login_response = client.post("/api/users/login", data=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/users/me", headers=headers)
        assert me_response.status_code == 200
        user_info = me_response.json()
        assert user_info["username"] == user_data["username"]
        assert user_info["email"] == user_data["email"]

    def test_multiple_users_registration(self, client):
        """Test registering multiple different users"""
        users = [
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "Password123",
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password": "Password456",
            },
            {
                "username": "user3",
                "email": "user3@example.com",
                "password": "Password789",
            },
        ]

        for user_data in users:
            response = client.post("/api/users/register", json=user_data)
            assert response.status_code == 201
            assert response.json()["username"] == user_data["username"]
