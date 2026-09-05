from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_analyze_endpoint_end_to_end_success():
    payload = {
        "repo_url": str(settings.BACKEND_DIR),
        "branch": "main",
        "task_description": "Add a CSV export endpoint for user transaction history."
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["job_id"].startswith("job_")
    assert data["status"] == "completed"
    
    # Verify report metrics
    report = data["report"]
    assert "overall_health_score" in report
    assert "verdict" in report
    assert report["ai_solvability"]["score"] >= 0
    assert len(report["ai_solvability"]["contributing_evidence"]) > 0
    
    # Verify candidate simulations
    simulations = data["simulations"]
    assert len(simulations) == 3
    
    # Verify recommendation
    recommendations = data["recommendations"]
    assert "upgraded_task" in recommendations
    assert len(recommendations["added_constraints"]) > 0

def test_analyze_endpoint_invalid_github_url_rejection():
    payload = {
        "repo_url": "https://invalid-domain.com/bad/repo",
        "task_description": "Add feature x to repository."
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422
    assert "Invalid GitHub URL" in response.text

def test_analyze_endpoint_short_task_description_rejection():
    payload = {
        "repo_url": "https://github.com/fastapi/fastapi",
        "task_description": "Too short"
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422
