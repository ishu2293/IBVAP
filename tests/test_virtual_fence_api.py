import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_list_fences(client):
    response = client.get("/api/fences")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_api_create_and_delete_fence(client):
    payload = {
        "name": "Integration Test Polygon",
        "type": "polygon",
        "points": [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9]],
        "camera_id": "CAM-01",
        "enabled": True,
        "severity": "HIGH"
    }
    create_res = client.post("/api/fences", json=payload)
    assert create_res.status_code == 200
    fence = create_res.json()
    assert fence["name"] == "Integration Test Polygon"
    fence_id = fence["id"]

    # Toggle fence
    toggle_res = client.post(f"/api/fences/{fence_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["enabled"] is False

    # Delete fence
    del_res = client.delete(f"/api/fences/{fence_id}")
    assert del_res.status_code == 200

def test_api_intrusions_and_stats(client):
    intrusions_res = client.get("/api/fences/intrusions")
    assert intrusions_res.status_code == 200
    assert isinstance(intrusions_res.json(), list)

    stats_res = client.get("/api/fences/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_fences" in stats
    assert "active_intrusions" in stats
