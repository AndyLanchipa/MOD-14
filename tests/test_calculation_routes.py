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
        "username": "calcuser",
        "email": "calc@example.com",
        "password": "CalcPass123",
    }


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Get authentication headers for a registered user"""
    # Register user
    client.post("/api/users/register", json=sample_user_data)

    # Login to get token
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    response = client.post("/api/users/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user_headers(client):
    """Get authentication headers for a second user"""
    user_data = {
        "username": "seconduser",
        "email": "second@example.com",
        "password": "SecondPass123",
    }
    # Register second user
    client.post("/api/users/register", json=user_data)

    # Login to get token
    login_data = {"username": user_data["username"], "password": user_data["password"]}
    response = client.post("/api/users/login", data=login_data)
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


class TestCalculationCreate:
    """Tests for creating calculations (Add)"""

    def test_create_calculation_addition(self, client, auth_headers):
        """Test creating an addition calculation"""
        calculation_data = {"a": 10.5, "b": 5.5, "type": "ADD"}
        response = client.post(
            "/api/calculations", json=calculation_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["a"] == 10.5
        assert data["b"] == 5.5
        assert data["type"] == "ADD"
        assert data["result"] == 16.0
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data

    def test_create_calculation_subtraction(self, client, auth_headers):
        """Test creating a subtraction calculation"""
        calculation_data = {"a": 20.0, "b": 8.0, "type": "SUB"}
        response = client.post(
            "/api/calculations", json=calculation_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 12.0

    def test_create_calculation_multiplication(self, client, auth_headers):
        """Test creating a multiplication calculation"""
        calculation_data = {"a": 6.0, "b": 7.0, "type": "MULTIPLY"}
        response = client.post(
            "/api/calculations", json=calculation_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 42.0

    def test_create_calculation_division(self, client, auth_headers):
        """Test creating a division calculation"""
        calculation_data = {"a": 15.0, "b": 3.0, "type": "DIVIDE"}
        response = client.post(
            "/api/calculations", json=calculation_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 5.0

    def test_create_calculation_division_by_zero(self, client, auth_headers):
        """Test creating a division by zero calculation fails validation"""
        calculation_data = {"a": 10.0, "b": 0.0, "type": "DIVIDE"}
        response = client.post(
            "/api/calculations", json=calculation_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_calculation_no_auth(self, client):
        """Test creating calculation without authentication fails"""
        calculation_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        response = client.post("/api/calculations", json=calculation_data)

        assert response.status_code == 401

    def test_create_calculation_invalid_type(self, client, auth_headers):
        """Test creating calculation with invalid type"""
        calculation_data = {"a": 10.0, "b": 5.0, "type": "INVALID"}
        response = client.post(
            "/api/calculations", json=calculation_data, headers=auth_headers
        )

        assert response.status_code == 422


class TestCalculationBrowse:
    """Tests for browsing calculations (Browse)"""

    def test_get_calculations_empty(self, client, auth_headers):
        """Test getting calculations when none exist"""
        response = client.get("/api/calculations", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_get_calculations_list(self, client, auth_headers):
        """Test getting list of calculations"""
        # Create multiple calculations
        calculations = [
            {"a": 10.0, "b": 5.0, "type": "ADD"},
            {"a": 20.0, "b": 8.0, "type": "SUB"},
            {"a": 6.0, "b": 7.0, "type": "MULTIPLY"},
        ]

        for calc in calculations:
            client.post("/api/calculations", json=calc, headers=auth_headers)

        # Get all calculations
        response = client.get("/api/calculations", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verify they're ordered by created_at desc (most recent first)
        assert data[0]["type"] == "MULTIPLY"
        assert data[1]["type"] == "SUB"
        assert data[2]["type"] == "ADD"

    def test_get_calculations_pagination(self, client, auth_headers):
        """Test pagination of calculations"""
        # Create 5 calculations
        for i in range(5):
            calc = {"a": float(i), "b": 1.0, "type": "ADD"}
            client.post("/api/calculations", json=calc, headers=auth_headers)

        # Get first 2
        response = client.get("/api/calculations?skip=0&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Get next 2
        response = client.get("/api/calculations?skip=2&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Get last 1
        response = client.get("/api/calculations?skip=4&limit=2", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_calculations_user_isolation(
        self, client, auth_headers, second_user_headers
    ):
        """Test that users only see their own calculations"""
        # User 1 creates calculations
        calc1 = {"a": 10.0, "b": 5.0, "type": "ADD"}
        client.post("/api/calculations", json=calc1, headers=auth_headers)

        # User 2 creates calculations
        calc2 = {"a": 20.0, "b": 10.0, "type": "SUB"}
        client.post("/api/calculations", json=calc2, headers=second_user_headers)

        # User 1 should only see their calculation
        response1 = client.get("/api/calculations", headers=auth_headers)
        assert len(response1.json()) == 1
        assert response1.json()[0]["type"] == "ADD"

        # User 2 should only see their calculation
        response2 = client.get("/api/calculations", headers=second_user_headers)
        assert len(response2.json()) == 1
        assert response2.json()[0]["type"] == "SUB"

    def test_get_calculations_no_auth(self, client):
        """Test getting calculations without authentication fails"""
        response = client.get("/api/calculations")

        assert response.status_code == 401


class TestCalculationRead:
    """Tests for reading specific calculation (Read)"""

    def test_get_calculation_by_id(self, client, auth_headers):
        """Test getting a specific calculation by ID"""
        # Create a calculation
        calc_data = {"a": 15.0, "b": 3.0, "type": "DIVIDE"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Get the calculation
        response = client.get(f"/api/calculations/{calc_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == calc_id
        assert data["a"] == 15.0
        assert data["b"] == 3.0
        assert data["result"] == 5.0

    def test_get_calculation_not_found(self, client, auth_headers):
        """Test getting non-existent calculation"""
        response = client.get("/api/calculations/99999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_calculation_wrong_user(
        self, client, auth_headers, second_user_headers
    ):
        """Test getting another user's calculation fails"""
        # User 1 creates a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # User 2 tries to access it
        response = client.get(
            f"/api/calculations/{calc_id}", headers=second_user_headers
        )

        assert response.status_code == 404

    def test_get_calculation_no_auth(self, client, auth_headers):
        """Test getting calculation without authentication"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Try to get without auth
        response = client.get(f"/api/calculations/{calc_id}")

        assert response.status_code == 401


class TestCalculationEdit:
    """Tests for editing calculations (Edit)"""

    def test_update_calculation_partial(self, client, auth_headers):
        """Test partially updating a calculation"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Update only 'a' value
        update_data = {"a": 20.0}
        response = client.patch(
            f"/api/calculations/{calc_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["a"] == 20.0
        assert data["b"] == 5.0  # Unchanged
        assert data["result"] == 25.0  # Recalculated

    def test_update_calculation_all_fields(self, client, auth_headers):
        """Test updating all calculation fields"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Update all fields
        update_data = {"a": 30.0, "b": 6.0, "type": "MULTIPLY"}
        response = client.patch(
            f"/api/calculations/{calc_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["a"] == 30.0
        assert data["b"] == 6.0
        assert data["type"] == "MULTIPLY"
        assert data["result"] == 180.0

    def test_update_calculation_not_found(self, client, auth_headers):
        """Test updating non-existent calculation"""
        update_data = {"a": 20.0}
        response = client.patch(
            "/api/calculations/99999", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_calculation_wrong_user(
        self, client, auth_headers, second_user_headers
    ):
        """Test updating another user's calculation fails"""
        # User 1 creates a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # User 2 tries to update it
        update_data = {"a": 20.0}
        response = client.patch(
            f"/api/calculations/{calc_id}",
            json=update_data,
            headers=second_user_headers,
        )

        assert response.status_code == 404

    def test_update_calculation_division_by_zero(self, client, auth_headers):
        """Test updating to division by zero fails validation"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "DIVIDE"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Try to update b to 0
        update_data = {"b": 0.0}
        response = client.patch(
            f"/api/calculations/{calc_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_update_calculation_no_auth(self, client, auth_headers):
        """Test updating calculation without authentication"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Try to update without auth
        update_data = {"a": 20.0}
        response = client.patch(f"/api/calculations/{calc_id}", json=update_data)

        assert response.status_code == 401


class TestCalculationDelete:
    """Tests for deleting calculations (Delete)"""

    def test_delete_calculation(self, client, auth_headers):
        """Test deleting a calculation"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/calculations/{calc_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/calculations/{calc_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_calculation_not_found(self, client, auth_headers):
        """Test deleting non-existent calculation"""
        response = client.delete("/api/calculations/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_calculation_wrong_user(
        self, client, auth_headers, second_user_headers
    ):
        """Test deleting another user's calculation fails"""
        # User 1 creates a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # User 2 tries to delete it
        response = client.delete(
            f"/api/calculations/{calc_id}", headers=second_user_headers
        )

        assert response.status_code == 404

        # Verify it still exists for user 1
        get_response = client.get(f"/api/calculations/{calc_id}", headers=auth_headers)
        assert get_response.status_code == 200

    def test_delete_calculation_no_auth(self, client, auth_headers):
        """Test deleting calculation without authentication"""
        # Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        calc_id = create_response.json()["id"]

        # Try to delete without auth
        response = client.delete(f"/api/calculations/{calc_id}")

        assert response.status_code == 401


class TestCalculationEndToEnd:
    """End-to-end tests for calculation CRUD workflow"""

    def test_complete_crud_workflow(self, client, auth_headers):
        """Test complete CRUD workflow for calculations"""
        # 1. Create a calculation
        calc_data = {"a": 10.0, "b": 5.0, "type": "ADD"}
        create_response = client.post(
            "/api/calculations", json=calc_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        calc_id = create_response.json()["id"]

        # 2. Read the calculation
        read_response = client.get(f"/api/calculations/{calc_id}", headers=auth_headers)
        assert read_response.status_code == 200
        assert read_response.json()["result"] == 15.0

        # 3. Update the calculation
        update_data = {"a": 20.0, "type": "MULTIPLY"}
        update_response = client.patch(
            f"/api/calculations/{calc_id}", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["result"] == 100.0

        # 4. Browse calculations
        browse_response = client.get("/api/calculations", headers=auth_headers)
        assert browse_response.status_code == 200
        assert len(browse_response.json()) == 1

        # 5. Delete the calculation
        delete_response = client.delete(
            f"/api/calculations/{calc_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204

        # 6. Verify deletion
        verify_response = client.get(
            f"/api/calculations/{calc_id}", headers=auth_headers
        )
        assert verify_response.status_code == 404

    def test_multiple_calculations_workflow(self, client, auth_headers):
        """Test creating and managing multiple calculations"""
        # Create multiple calculations
        calculations = [
            {"a": 10.0, "b": 2.0, "type": "ADD"},
            {"a": 20.0, "b": 5.0, "type": "SUB"},
            {"a": 6.0, "b": 7.0, "type": "MULTIPLY"},
            {"a": 100.0, "b": 4.0, "type": "DIVIDE"},
        ]

        created_ids = []
        for calc in calculations:
            response = client.post("/api/calculations", json=calc, headers=auth_headers)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Browse all calculations
        browse_response = client.get("/api/calculations", headers=auth_headers)
        assert len(browse_response.json()) == 4

        # Update first calculation
        update_response = client.patch(
            f"/api/calculations/{created_ids[0]}",
            json={"a": 50.0},
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Delete last two calculations
        for calc_id in created_ids[-2:]:
            delete_response = client.delete(
                f"/api/calculations/{calc_id}", headers=auth_headers
            )
            assert delete_response.status_code == 204

        # Verify only 2 remain
        final_browse = client.get("/api/calculations", headers=auth_headers)
        assert len(final_browse.json()) == 2
