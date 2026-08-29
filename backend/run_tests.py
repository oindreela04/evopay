"""Self-contained test runner for EvoPay AI."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

import database
from main import app
from ml.feature_engineering import to_features
from ml.predict import predict


class EvoPayAiApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_db = Path(cls.temp_dir.name) / "test.db"
        database.DATABASE_PATH = cls.test_db
        database.create_db_and_tables()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "service": "evopay-ai"})

    def test_02_dashboard(self):
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("metrics", data)
        self.assertIn("transactions", data)
        self.assertIn("incidents", data)

    def test_03_transactions_pagination(self):
        res = self.client.get("/api/transactions?limit=2&offset=0")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 2)

    def test_04_transaction_detail(self):
        res = self.client.get("/api/transactions/TXN-84921")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["amount"], 12840)

    def test_05_transaction_risk(self):
        res = self.client.get("/api/transactions/TXN-84921/risk")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("risk_score", data)
        self.assertIn("classification", data)
        self.assertIn("signals", data)
        self.assertIn("reasons", data)

    def test_06_transaction_analysis_incident_creation(self):
        res = self.client.post("/api/transactions/TXN-84921/analyze")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["recommended_action"], "BLOCK")
        incidents = self.client.get("/api/incidents").json()
        self.assertTrue(any(item["status"] == "OPEN" for item in incidents))

    def test_07_transaction_actions(self):
        for action in ("ALLOW", "VERIFY", "HOLD", "BLOCK"):
            res = self.client.post("/api/transactions/TXN-84918/action", json={"action": action})
            self.assertEqual(res.status_code, 200)
            self.assertIn(res.json()["status"], {"ALLOWED", "VERIFY", "HOLD", "BLOCKED"})

    def test_08_attack_generation(self):
        res = self.client.post("/api/attacks/generate", json={"attack_type": "synthetic_identity", "strategy": "Synthetic Identity"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["attack_type"], "synthetic_identity")
        self.assertEqual(res.json()["generation"], 1)

    def test_09_attack_evolution(self):
        attack = self.client.post("/api/attacks/generate", json={"attack_type": "behavioral_mimicry"}).json()
        res = self.client.post("/api/attacks/evolve", json={"attack_id": attack["id"]})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["generation"], 2)

    def test_10_network_and_investigation(self):
        graph = self.client.get("/api/network")
        self.assertEqual(graph.status_code, 200)
        self.assertTrue(len(graph.json()["nodes"]) > 0)
        self.assertTrue(len(graph.json()["relationships"]) > 0)
        inv = self.client.post("/api/investigate", json={"transaction_id": "TXN-84921"})
        self.assertEqual(inv.status_code, 200)
        self.assertEqual(inv.json()["investigation"]["recommended_action"], "BLOCK")

    def test_11_simulation_lifecycle(self):
        started = self.client.post("/api/simulation/start", json={})
        self.assertEqual(started.status_code, 200)
        sim_id = started.json()["id"]
        current = self.client.get(f"/api/simulation/{sim_id}")
        self.assertEqual(current.status_code, 200)
        self.assertEqual(current.json()["status"], "RUNNING")

    def test_12_incident_actions(self):
        incidents = self.client.get("/api/incidents").json()
        self.assertTrue(len(incidents) > 0)
        inc_id = incidents[0]["id"]
        res = self.client.post(f"/api/incidents/{inc_id}/action", json={"status": "INVESTIGATING"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "INVESTIGATING")

    def test_13_threat_library_and_adaptation(self):
        pattern = self.client.post("/api/threat-library", json={"name": "QA Pattern", "description": "Synthetic QA pattern", "severity": "HIGH"})
        self.assertEqual(pattern.status_code, 200)
        adapted = self.client.post("/api/defense/adapt", json={"pattern": "DEFENSE BLIND SPOT"})
        self.assertEqual(adapted.status_code, 200)
        self.assertGreater(adapted.json()["after_detection"], adapted.json()["before_detection"])

    def test_14_analytics_and_audit(self):
        analytics = self.client.get("/api/analytics")
        self.assertEqual(analytics.status_code, 200)
        self.assertIn("detection_rate", analytics.json())
        self.assertIn("daily_events", analytics.json())
        audit = self.client.get("/api/audit")
        self.assertEqual(audit.status_code, 200)
        self.assertIsInstance(audit.json(), list)

    def test_15_feature_engineering_consistency(self):
        sample = {
            "amount": 15000,
            "location": "Mumbai",
            "payment_method": "UPI",
            "transaction_velocity": 4.5,
            "account_age_days": 120,
        }
        features = to_features(sample)
        self.assertEqual(features.shape[0], 1)
        self.assertIn("location_code", features.columns)
        self.assertIn("payment_method_code", features.columns)

    def test_16_ml_prediction_pipeline(self):
        sample = {
            "amount": 45000,
            "location": "Delhi",
            "payment_method": "Card",
            "transaction_velocity": 12.0,
            "failed_attempts": 4,
            "device_changes": 3,
        }
        result = predict(sample)
        self.assertIn("ml_score", result)
        self.assertIn("anomaly_score", result)
        self.assertTrue(0 <= result["ml_score"] <= 100)
        self.assertTrue(0 <= result["anomaly_score"] <= 100)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvoPayAiApiTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
