"""
Tests for authentication functionality.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apps.api.app.main import app
from apps.api.app.core.database import get_db, Base

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_register_user(client):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "sales"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["role"] == user_data["role"]
    assert "id" in data
    assert "hashed_password" not in data  # Should not expose password


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser1",
        "password": "testpassword123",
        "role": "sales"
    }
    
    # Register first user
    client.post("/auth/register", json=user_data)
    
    # Try to register with same email
    user_data["username"] = "testuser2"
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    user_data = {
        "email": "test1@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": "sales"
    }
    
    # Register first user
    client.post("/auth/register", json=user_data)
    
    # Try to register with same username
    user_data["email"] = "test2@example.com"
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


def test_login_success(client):
    """Test successful login."""
    # Register user first
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": "sales"
    }
    client.post("/auth/register", json=user_data)
    
    # Login with form data (OAuth2)
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_success(client):
    """Test successful login with JSON."""
    # Register user first
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": "sales"
    }
    client.post("/auth/register", json=user_data)
    
    # Login with JSON
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post("/auth/login-json", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user(client):
    """Test getting current user profile."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": "sales"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Get user profile
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_unauthorized_access(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 401


def get_token_for_role(client, role: str) -> str:
    """Helper function to get token for a user with specific role."""
    user_data = {
        "email": f"{role}@example.com",
        "username": f"{role}user",
        "password": "testpassword123",
        "role": role
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": f"{role}user",
        "password": "testpassword123"
    }
    login_response = client.post("/auth/login", data=login_data)
    return login_response.json()["access_token"]


def test_admin_access_users_list(client):
    """Test admin can access users list."""
    token = get_token_for_role(client, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_non_admin_access_users_list(client):
    """Test non-admin cannot access users list."""
    token = get_token_for_role(client, "sales")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/users/", headers=headers)
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def test_admin_create_user(client):
    """Test admin can create new users."""
    token = get_token_for_role(client, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    
    new_user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
        "role": "marketer"
    }
    
    response = client.post("/users/", json=new_user_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == new_user_data["email"]
    assert data["role"] == new_user_data["role"]


def test_admin_get_user_by_id(client):
    """Test admin can get user by ID."""
    # Create admin and get token
    token = get_token_for_role(client, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test user to retrieve
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": "sales"
    }
    create_response = client.post("/users/", json=user_data, headers=headers)
    user_id = create_response.json()["id"]
    
    # Get user by ID
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]


def test_admin_update_user(client):
    """Test admin can update users."""
    # Create admin and get token
    token = get_token_for_role(client, "admin")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test user to update
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": "sales"
    }
    create_response = client.post("/users/", json=user_data, headers=headers)
    user_id = create_response.json()["id"]
    
    # Update user
    update_data = {
        "role": "marketer",
        "full_name": "Updated Name"
    }
    response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["role"] == "marketer"
    assert data["full_name"] == "Updated Name"