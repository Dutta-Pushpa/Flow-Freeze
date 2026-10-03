import pytest
pytest.importorskip("fastapi"); pytest.importorskip("httpx")
from fastapi.testclient import TestClient

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("FLOWFREEZE_API_TOKENS", "a1:analyst,v1:viewer")
    from backend.main import app; return TestClient(app)
BODY = {"incident_id": "INC-2407", "wallet_id": "W4", "reported_amount": 15000, "wallet_balance": 22000, "new_relationship": 1, "rapid_forwarding": 1, "receiver_age_days": 25}

def test_health_open_but_everything_else_needs_a_token(client):
    assert client.get("/health").status_code == 200
    assert client.post("/api/v1/interventions/recommend", json=BODY).status_code == 401
    assert client.post("/api/v1/interventions/recommend", json=BODY, headers={"Authorization": "Bearer wrong"}).status_code == 401
def test_viewer_is_forbidden_analyst_allowed(client):
    assert client.post("/api/v1/interventions/recommend", json=BODY, headers={"Authorization": "Bearer v1"}).status_code == 403
    r = client.post("/api/v1/interventions/recommend", json=BODY, headers={"Authorization": "Bearer a1"}); assert r.status_code == 200
    j = r.json(); assert j["recommendation"]["requires_human_approval"] and j["explanation"]["factors"] and set(j["grounding"]["narrative"]) == {"what_happened", "why_risky", "what_next"}
def test_invalid_input_rejected(client):
    assert client.post("/api/v1/incidents/score", json={**BODY, "reported_amount": -5}, headers={"Authorization": "Bearer a1"}).status_code == 422
