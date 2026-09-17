from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_tickets"] == 500

def test_nl_query_endpoint():
    response = client.post("/api/v1/query", json={
        "query": "How many tickets are currently open?",
        "mode": "auto",
        "role": "admin"
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "execution_mode" in data

def test_anomalies_endpoint():
    response = client.get("/api/v1/anomalies?role=admin")
    assert response.status_code == 200
    data = response.json()
    assert "total_anomalies" in data
    assert "narrative_summary" in data

def test_tickets_endpoint():
    response = client.get("/api/v1/tickets?limit=10&offset=0&role=admin")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 10
    assert len(data["tickets"]) == 10
