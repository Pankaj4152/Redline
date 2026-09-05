from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to Redline API Engine" in response.json()["message"]

def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == settings.APP_NAME

def test_settings_configuration():
    assert settings.APP_NAME == "Redline Backend"
    assert settings.USE_MOCK_LLM is True
    assert isinstance(settings.CORS_ORIGINS, list)
    assert "http://localhost:5173" in settings.CORS_ORIGINS

def test_cors_headers():
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
