import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from main import app, get_session
from models.user import User
from models.product import Product

# Create a test database
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def client():
    \"\"\"Create a test client for the FastAPI app.\"\"\"
    # Create test engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    # Override the database dependency
    def get_test_session():
        with Session(engine) as session:
            yield session
    
    app.dependency_overrides[get_session] = get_test_session
    
    yield TestClient(app)
    
    # Cleanup after tests
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def test_user():
    \"\"\"Create a test user for authentication tests.\"\"\"
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "user"
    }

@pytest.fixture
def test_admin():
    \"\"\"Create a test admin for authentication tests.\"\"\"
    return {
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
        "role": "admin"
    }

@pytest.fixture
def auth_headers(client, test_user):
    \"\"\"Get authentication headers for protected endpoints.\"\"\"
    # Register user
    client.post("/register", json=test_user)
    
    # Login
    response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(client, test_admin):
    \"\"\"Get authentication headers for admin endpoints.\"\"\"
    # Register admin
    client.post("/register", json=test_admin)
    
    # Login
    response = client.post(
        "/login",
        data={"username": test_admin["username"], "password": test_admin["password"]}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
