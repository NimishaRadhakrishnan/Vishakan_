import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app import models


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency in FastAPI app
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Setup database override
    app.dependency_overrides[get_db] = override_get_db
    print("DEBUG: Base metadata tables in test_auth:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup override
    app.dependency_overrides.pop(get_db, None)
    # Teardown database
    Base.metadata.drop_all(bind=engine)
    try:
        import os
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    except Exception:
        pass

client = TestClient(app)

def test_register_farmer():
    payload = {
        "name": "Arun Prasad",
        "mobile": "9876543210",
        "password": "farmerpassword",
        "district": "Coimbatore",
        "state": "Tamil Nadu",
        "language": "Tamil",
        "role": "Farmer"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Arun Prasad"
    assert data["mobile"] == "9876543210"
    assert data["role"] == "Farmer"

def test_register_duplicate_mobile():
    payload = {
        "name": "Arun Duplicate",
        "mobile": "9876543210",
        "password": "otherpassword",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "language": "English",
        "role": "Farmer"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Mobile number already registered"

def test_login_success():
    payload = {
        "mobile": "9876543210",
        "password": "farmerpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "Farmer"

def test_login_invalid_credentials():
    payload = {
        "mobile": "9876543210",
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect mobile number or password"

def test_get_me_profile():
    # Login to get token
    payload = {
        "mobile": "9876543210",
        "password": "farmerpassword"
    }
    login_response = client.post("/api/auth/login", json=payload)
    token = login_response.json()["access_token"]
    
    # Use token to access /me
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    data = me_response.json()
    assert data["mobile"] == "9876543210"
    assert data["name"] == "Arun Prasad"
