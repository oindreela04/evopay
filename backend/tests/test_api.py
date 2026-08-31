from fastapi.testclient import TestClient
import pytest
import os
import sqlite3
import tempfile
from pathlib import Path

import database
import auth
from main import app
from ml.feature_engineering import to_features
from ml.predict import predict

PASSWORD = "correct-horse-42"


def authenticate(test_client: TestClient, email: str = "analyst@example.com", display_name: str = "Test Analyst") -> dict:
    response = test_client.post("/api/auth/signup", json={"email": email, "password": PASSWORD, "display_name": display_name})
    assert response.status_code == 201, response.text
    test_client.headers.update({"X-CSRF-Token": test_client.cookies.get(auth.CSRF_COOKIE)})
    return response.json()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_db)
    auth.clear_rate_limits()
    with TestClient(app) as test_client:
        user = authenticate(test_client)
        with database.get_connection() as connection:
            connection.execute("INSERT INTO customers (id, name, city, user_id) VALUES (?, ?, ?, ?)", ("C-TEST", "Synthetic test customer", "Test City", user["id"]))
            connection.execute("INSERT INTO merchants (id, name, city, user_id) VALUES (?, ?, ?, ?)", ("M-TEST", "Synthetic test merchant", "Test City", user["id"]))
            connection.execute("INSERT INTO devices (id, platform, risk_score, user_id) VALUES (?, ?, ?, ?)", ("D-TEST", "Test device", 90, user["id"]))
            connection.executemany("INSERT INTO transactions (id, customer_id, merchant_id, amount, location, payment_method, risk_score, status, device_id, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
                ("TXN-HIGH", "C-TEST", "M-TEST", 12840, "Test City", "Test", 94, "BLOCKED", "D-TEST", "2026-01-01T00:00:00Z", user["id"]),
                ("TXN-LOW", "C-TEST", "M-TEST", 1280, "Test City", "Test", 22, "ALLOWED", "D-TEST", "2026-01-01T00:01:00Z", user["id"]),
            ])
            connection.execute("INSERT INTO incidents (id, title, severity, status, created_at, transaction_id, risk_score, reasons, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("INC-TEST", "Fixture incident", "HIGH", "OPEN", "2026-01-01T00:02:00Z", "TXN-HIGH", 94, "[]", user["id"]))
            connection.commit()
        yield test_client


@pytest.fixture()
def empty_client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "empty.db")
    auth.clear_rate_limits()
    with TestClient(app) as test_client:
        authenticate(test_client)
        yield test_client


def test_empty_database_returns_honest_empty_state(empty_client):
    dashboard = empty_client.get("/api/dashboard").json()
    assert dashboard["metrics"] == {
        "transactions_monitored": 0,
        "active_threats": 0,
        "attacks_simulated": 0,
        "mean_detection_score": None,
        "false_positive_rate": None,
        "average_detection_time": None,
    }
    assert dashboard["transactions"] == []
    assert dashboard["incidents"] == []
    assert empty_client.get("/api/transactions").json() == []
    assert empty_client.get("/api/network").json() == {"nodes": [], "relationships": []}
    assert empty_client.get("/api/analytics").json() == {
        "mean_detection_score": None,
        "false_positive_rate": None,
        "average_response_time": None,
        "daily_events": [],
        "model_version": None,
    }


def test_authentication_lifecycle_and_validation(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "auth.db")
    auth.clear_rate_limits()
    with TestClient(app) as test_client:
        created = test_client.post("/api/auth/signup", json={"email": "  Analyst@Example.COM ", "password": PASSWORD, "display_name": "Analyst"})
        assert created.status_code == 201
        assert created.json()["email"] == "analyst@example.com"
        assert auth.SESSION_COOKIE in created.cookies and created.cookies[auth.SESSION_COOKIE]
        with database.get_connection() as connection:
            stored = connection.execute("SELECT email, password_hash FROM users").fetchone()
            session = connection.execute("SELECT token_hash FROM user_sessions").fetchone()
        assert stored["email"] == "analyst@example.com"
        assert stored["password_hash"].startswith("$argon2id$") and PASSWORD not in stored["password_hash"]
        assert session["token_hash"] != created.cookies[auth.SESSION_COOKIE]
        duplicate = test_client.post("/api/auth/signup", json={"email": "ANALYST@example.com", "password": PASSWORD, "display_name": "Other"})
        assert duplicate.status_code == 409
        test_client.cookies.clear()
        assert test_client.post("/api/auth/login", json={"email": "analyst@example.com", "password": "incorrect-pass-9"}).status_code == 401
        login = test_client.post("/api/auth/login", json={"email": "analyst@example.com", "password": PASSWORD})
        assert login.status_code == 200
        assert test_client.get("/api/auth/me").json()["email"] == "analyst@example.com"
        restored_cookies = dict(test_client.cookies)
        with TestClient(app) as restored_client:
            restored_client.cookies.update(restored_cookies)
            assert restored_client.get("/api/auth/me").json()["email"] == "analyst@example.com"
        csrf = test_client.cookies.get(auth.CSRF_COOKIE)
        assert test_client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf}).status_code == 204
        assert test_client.get("/api/auth/me").status_code == 401
        with TestClient(app) as invalidated_client:
            invalidated_client.cookies.update(restored_cookies)
            assert invalidated_client.get("/api/auth/me").status_code == 401


def test_expired_session_csrf_and_rate_limiting(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "security.db")
    auth.clear_rate_limits()
    with TestClient(app) as test_client:
        authenticate(test_client, "security@example.com")
        assert test_client.post("/api/attacks/generate", json={"attack_type": "account_takeover"}, headers={"X-CSRF-Token": "wrong"}).status_code == 403
        with database.get_connection() as connection:
            connection.execute("UPDATE user_sessions SET expires_at = ?", ("2000-01-01T00:00:00+00:00",))
            connection.commit()
        assert test_client.get("/api/auth/me").status_code == 401
        test_client.cookies.clear()
        for _ in range(5):
            assert test_client.post("/api/auth/login", json={"email": "security@example.com", "password": "bad-password-1"}).status_code == 401
        limited = test_client.post("/api/auth/login", json={"email": "security@example.com", "password": "bad-password-1"})
        assert limited.status_code == 429
        for _ in range(3):
            assert test_client.post("/api/auth/signup", json={"email": "security@example.com", "password": PASSWORD, "display_name": "Duplicate"}).status_code == 409
        assert test_client.post("/api/auth/signup", json={"email": "security@example.com", "password": PASSWORD, "display_name": "Duplicate"}).status_code == 429


def test_unauthenticated_rejection_and_user_isolation(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "ownership.db")
    auth.clear_rate_limits()
    with TestClient(app) as test_client:
        assert test_client.get("/api/dashboard").status_code == 401
        assert test_client.get("/api/health").status_code == 200
        user_a = authenticate(test_client, "a@example.com", "User A")
        cookies_a = dict(test_client.cookies)
        csrf_a = cookies_a[auth.CSRF_COOKIE]
        attack_a = test_client.post("/api/attacks/generate", json={"attack_type": "account_takeover"}).json()
        transaction_a = test_client.get("/api/transactions").json()[0]
        with database.get_connection() as connection:
            connection.execute("INSERT INTO incidents (id, title, severity, status, created_at, transaction_id, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)", ("INC-A", "Owned incident", "HIGH", "OPEN", "2026-01-01T00:00:00Z", transaction_a["id"], user_a["id"]))
            connection.commit()
        incident_a = test_client.get("/api/incidents").json()[0]
        simulation_a = test_client.post("/api/simulation/start", json={"attack_id": attack_a["id"]}).json()
        test_client.cookies.clear()
        user_b = authenticate(test_client, "b@example.com", "User B")
        assert user_a["id"] != user_b["id"]
        assert test_client.get("/api/transactions").json() == []
        assert test_client.get("/api/attacks").json() == []
        assert test_client.get("/api/network").json() == {"nodes": [], "relationships": []}
        assert test_client.get("/api/analytics").json()["daily_events"] == []
        assert test_client.get(f"/api/transactions/{transaction_a['id']}").status_code == 404
        assert test_client.post(f"/api/transactions/{transaction_a['id']}/action", json={"action": "BLOCK"}).status_code == 404
        assert test_client.post("/api/attacks/evolve", json={"attack_id": attack_a["id"]}).status_code == 404
        assert test_client.post("/api/simulation/start", json={"attack_id": attack_a["id"]}).status_code == 404
        assert test_client.get(f"/api/simulation/{simulation_a['id']}").status_code == 404
        assert test_client.post(f"/api/incidents/{incident_a['id']}/action", json={"status": "RESOLVED"}).status_code == 404
        assert test_client.get("/api/audit").json() == []
        test_client.cookies.clear()
        test_client.cookies.update(cookies_a)
        test_client.headers.update({"X-CSRF-Token": csrf_a})
        assert len(test_client.get("/api/transactions").json()) == attack_a["transactions"]
        with database.get_connection() as connection:
            connection.execute("INSERT INTO attacks (id, name, severity, status, accounts, devices, merchants, transactions, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("EV-LEGACY", "Legacy", "LOW", "STORED", 1, 1, 1, 1, "2020-01-01T00:00:00Z"))
            connection.commit()
        assert all(item["id"] != "EV-LEGACY" for item in test_client.get("/api/attacks").json())


def test_non_destructive_legacy_migration_leaves_records_unassigned(tmp_path, monkeypatch):
    legacy_db = tmp_path / "legacy.db"
    with sqlite3.connect(legacy_db) as connection:
        connection.execute("CREATE TABLE transactions (id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, merchant_id TEXT NOT NULL, amount INTEGER NOT NULL, location TEXT NOT NULL, payment_method TEXT NOT NULL, risk_score INTEGER NOT NULL, status TEXT NOT NULL, device_id TEXT NOT NULL, created_at TEXT NOT NULL)")
        connection.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("TXN-LEGACY", "C-OLD", "M-OLD", 100, "Lab", "TEST", 10, "ALLOWED", "D-OLD", "2020-01-01T00:00:00Z"))
    monkeypatch.setattr(database, "DATABASE_PATH", legacy_db)
    database.create_db_and_tables()
    with database.get_connection() as connection:
        record = connection.execute("SELECT id, user_id FROM transactions WHERE id = ?", ("TXN-LEGACY",)).fetchone()
    assert record["id"] == "TXN-LEGACY"
    assert record["user_id"] is None
def test_generated_attack_populates_related_views(empty_client):
    before_count = len(empty_client.get("/api/transactions?limit=200").json())
    attack = empty_client.post("/api/attacks/generate", json={"attack_type": "account_takeover", "strategy": "Account Takeover"}).json()
    transactions = empty_client.get("/api/transactions?limit=200").json()
    dashboard = empty_client.get("/api/dashboard").json()
    network = empty_client.get("/api/network").json()
    analytics = empty_client.get("/api/analytics").json()
    assert attack["synthetic"] is True
    assert attack["transactions"] == 19
    assert len(transactions) - before_count == attack["transactions"]
    assert all(item["synthetic"] is True and item["id"].startswith("SYN-TXN-") for item in transactions)
    assert dashboard["metrics"]["transactions_monitored"] == attack["transactions"]
    assert dashboard["metrics"]["attacks_simulated"] == 1
    assert dashboard["metrics"]["mean_detection_score"] == attack["detection_score"]
    assert network["nodes"] and network["relationships"]
    assert sum(item["count"] for item in analytics["daily_events"]) == attack["transactions"] + 1


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "evopay-ai"}


def test_fixture_and_pagination(client):
    response = client.get("/api/transactions?limit=2&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_transaction_detail(client):
    response = client.get("/api/transactions/TXN-HIGH")
    assert response.status_code == 200
    assert response.json()["amount"] == 12840


def test_transaction_risk_endpoint(client):
    response = client.get("/api/transactions/TXN-HIGH/risk")
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "classification" in data
    assert "signals" in data
    assert "reasons" in data


def test_transaction_analysis_creates_incident(client):
    response = client.post("/api/transactions/TXN-HIGH/analyze")
    assert response.status_code == 200
    assert response.json()["recommended_action"] == "BLOCK"
    incidents = client.get("/api/incidents").json()
    assert any(item["status"] == "OPEN" for item in incidents)


def test_transaction_actions(client):
    for action in ("ALLOW", "VERIFY", "HOLD", "BLOCK"):
        response = client.post("/api/transactions/TXN-LOW/action", json={"action": action})
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
    investigation = client.post("/api/investigate", json={"transaction_id": "TXN-HIGH"})
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
    assert adapted.json()["after_detection_score"] is None
    assert client.get("/api/threat-library").status_code == 200


def test_analytics_and_audit(client):
    analytics = client.get("/api/analytics")
    assert analytics.status_code == 200
    assert "mean_detection_score" in analytics.json()
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
