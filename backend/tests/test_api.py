from fastapi.testclient import TestClient
import pytest
import os
import tempfile
from pathlib import Path

import database
from main import app
from ml.feature_engineering import to_features
from ml.predict import predict


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_db)
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "evopay-ai"}


def test_database_seed_and_pagination(client):
    response = client.get("/api/transactions?limit=2&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_transaction_detail(client):
    response = client.get("/api/transactions/TXN-84921")
    assert response.status_code == 200
    assert response.json()["amount"] == 12840


def test_transaction_risk_endpoint(client):
    response = client.get("/api/transactions/TXN-84921/risk")
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "classification" in data
    assert "signals" in data
    assert "reasons" in data


def test_transaction_analysis_creates_incident(client):
    response = client.post("/api/transactions/TXN-84921/analyze")
    assert response.status_code == 200
    assert response.json()["recommended_action"] == "BLOCK"
    incidents = client.get("/api/incidents").json()
    assert any(item["status"] == "OPEN" for item in incidents)


def test_transaction_actions(client):
    for action in ("ALLOW", "VERIFY", "HOLD", "BLOCK"):
        response = client.post("/api/transactions/TXN-84918/action", json={"action": action})
        assert response.status_code == 200
        assert response.json()["status"] in {"ALLOWED", "VERIFY", "HOLD", "BLOCKED"}


def test_attack_generation(client):
    response = client.post("/api/attacks/generate", json={"attack_type": "synthetic_identity", "strategy": "Synthetic Identity"})
    assert response.status_code == 200
    assert response.json()["attack_type"] == "synthetic_identity"
    assert response.json()["generation"] == 1


def test_attack_evolution(client):
    attack = client.post("/api/attacks/generate", json={"attack_type": "behavioral_mimicry"}).json()
    response = client.post("/api/attacks/evolve", json={"attack_id": attack["id"]})
    assert response.status_code == 200
    assert response.json()["generation"] == 2


def test_network_and_investigation(client):
    graph = client.get("/api/network")
    assert graph.status_code == 200
    assert len(graph.json()["nodes"]) > 0
    assert len(graph.json()["relationships"]) > 0
    investigation = client.post("/api/investigate", json={"transaction_id": "TXN-84921"})
    assert investigation.status_code == 200
    assert investigation.json()["investigation"]["recommended_action"] == "BLOCK"


def test_simulation_lifecycle(client):
    started = client.post("/api/simulation/start", json={})
    assert started.status_code == 200
    simulation_id = started.json()["id"]
    current = client.get(f"/api/simulation/{simulation_id}")
    assert current.status_code == 200
    assert current.json()["status"] == "RUNNING"


def test_incident_actions(client):
    incidents = client.get("/api/incidents").json()
    assert len(incidents) > 0
    inc_id = incidents[0]["id"]
    update_res = client.post(f"/api/incidents/{inc_id}/action", json={"status": "INVESTIGATING"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "INVESTIGATING"


def test_threat_library_and_adaptation(client):
    pattern = client.post("/api/threat-library", json={"name": "QA Pattern", "description": "Synthetic QA pattern", "severity": "HIGH"})
    assert pattern.status_code == 200
    adapted = client.post("/api/defense/adapt", json={"pattern": "DEFENSE BLIND SPOT"})
    assert adapted.status_code == 200
    assert adapted.json()["after_detection"] > adapted.json()["before_detection"]
    assert client.get("/api/threat-library").status_code == 200


def test_analytics_and_audit(client):
    analytics = client.get("/api/analytics")
    assert analytics.status_code == 200
    assert "detection_rate" in analytics.json()
    assert "daily_events" in analytics.json()
    audit = client.get("/api/audit")
    assert audit.status_code == 200
    assert isinstance(audit.json(), list)


def test_feature_engineering_consistency():
    sample = {
        "amount": 15000,
        "location": "Mumbai",
        "payment_method": "UPI",
        "transaction_velocity": 4.5,
        "account_age_days": 120,
    }
    features = to_features(sample)
    assert features.shape[0] == 1
    assert "location_code" in features.columns
    assert "payment_method_code" in features.columns


def test_ml_prediction_pipeline():
    sample = {
        "amount": 45000,
        "location": "Delhi",
        "payment_method": "Card",
        "transaction_velocity": 12.0,
        "failed_attempts": 4,
        "device_changes": 3,
    }
    result = predict(sample)
    assert "ml_score" in result
    assert "anomaly_score" in result
    assert 0 <= result["ml_score"] <= 100
    assert 0 <= result["anomaly_score"] <= 100
