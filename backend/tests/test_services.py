import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app import models
from backend.app.models.product import Product

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_services.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_services_db():
    # Setup database override
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    
    # Pre-seed essential products for testing
    db = TestingSessionLocal()
    p1 = Product(
        product_name="V-NITRO",
        category="Bio Fertilizer",
        description="Nitrogen fixer",
        dosage="2.5 ml/L water",
        price=350.0,
        unit="500ml",
        suitable_crops=["Rice", "Banana"]
    )
    p2 = Product(
        product_name="V-CURE",
        category="Bio Fungicide",
        description="Bacterial fungicide",
        dosage="2.5 ml/L water",
        price=460.0,
        unit="500ml",
        suitable_crops=["Rice", "Tomato"]
    )
    db.add_all([p1, p2])
    db.commit()
    db.close()
    
    yield
    # Cleanup override
    app.dependency_overrides.pop(get_db, None)
    # Teardown database
    Base.metadata.drop_all(bind=engine)
    try:
        import os
        if os.path.exists("./test_services.db"):
            os.remove("./test_services.db")
    except Exception:
        pass

client = TestClient(app)

# Helper to get valid login token
def get_auth_headers():
    # Register user first
    reg_payload = {
        "name": "Test Farmer",
        "mobile": "9998887770",
        "password": "servicepassword",
        "district": "Coimbatore",
        "state": "Tamil Nadu",
        "language": "English",
        "role": "Farmer"
    }
    client.post("/api/auth/register", json=reg_payload)
    
    # Login
    login_payload = {
        "mobile": "9998887770",
        "password": "servicepassword"
    }
    res = client.post("/api/auth/login", json=login_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_crop_recommendation():
    headers = get_auth_headers()
    payload = {
        "soil_type": "Loamy",
        "nitrogen": 80.0,
        "phosphorus": 45.0,
        "potassium": 50.0,
        "ph": 6.5,
        "temperature": 28.5,
        "humidity": 75.0,
        "rainfall": 150.0
    }
    response = client.post("/api/crop/predict-crop", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_crop" in data
    assert "confidence_score" in data
    assert "top_3_alternative_crops" in data
    assert "recommended_products" in data

def test_soil_health_analysis():
    headers = get_auth_headers()
    payload = {
        "N": 60.0,
        "P": 30.0,
        "K": 40.0,
        "pH": 6.5,
        "OrganicCarbon": 0.55,
        "soil_type": "Loamy"
    }
    response = client.post("/api/crop/soil-health", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "soil_health_score" in data
    assert "deficiency_report" in data
    assert "fertilization_plan" in data

def test_product_recommendation():
    headers = get_auth_headers()
    payload = {
        "crop_name": "Rice",
        "crop_stage": "Vegetative",
        "soil_type": "Loamy"
    }
    response = client.post("/api/products/recommend", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_products" in data
    assert "dosage_instructions" in data
    assert "application_schedule" in data

def test_dosage_calculator():
    headers = get_auth_headers()
    payload = {
        "crop": "Rice",
        "product": "V-NITRO",
        "area": 2.5,
        "unit": "acres"
    }
    response = client.post("/api/products/dosage-calculator", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "required_quantity" in data
    assert "mixing_ratio" in data
    assert data["estimated_cost"] > 0
    assert data["water_volume_liters"] == 500

def test_chatbot_query():
    headers = get_auth_headers()
    payload = {
        "question": "What should I spray for blast in paddy?"
    }
    response = client.post("/api/chatbot/chat", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "recommended_products" in data
    assert "context_sources" in data

def test_analytics_endpoints():
    headers = get_auth_headers()
    # Test dashboard kpi endpoint
    res_kpi = client.get("/api/analytics/dashboard", headers=headers)
    assert res_kpi.status_code == 200
    data = res_kpi.json()
    assert "total_farmers" in data
    assert "chatbot_usage" in data
    
    # Test top products endpoint
    res_prod = client.get("/api/analytics/top-products", headers=headers)
    assert res_prod.status_code == 200
    assert len(res_prod.json()) >= 0
