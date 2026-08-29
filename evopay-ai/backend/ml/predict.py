from __future__ import annotations
from pathlib import Path
from typing import Any
import joblib
try:
    from .feature_engineering import to_features
except ImportError:
    from feature_engineering import to_features

MODEL_DIR = Path(__file__).parent / "models"


_FRAUD_MODEL = None
_ANOMALY_MODEL = None


def get_models():
    global _FRAUD_MODEL, _ANOMALY_MODEL
    model_path = MODEL_DIR / "fraud_model.joblib"
    anomaly_path = MODEL_DIR / "anomaly_model.joblib"
    if model_path.exists() and _FRAUD_MODEL is None:
        _FRAUD_MODEL = joblib.load(model_path)
    if anomaly_path.exists() and _ANOMALY_MODEL is None:
        _ANOMALY_MODEL = joblib.load(anomaly_path)
    return _FRAUD_MODEL, _ANOMALY_MODEL


def predict(transaction: dict[str, Any]) -> dict[str, float]:
    fraud_model, anomaly_model = get_models()
    if fraud_model is None or anomaly_model is None:
        amount = float(transaction.get("amount", 0) or 0)
        velocity = float(transaction.get("transaction_velocity", 0) or 0)
        failed = float(transaction.get("failed_attempts", 0) or 0)
        device_sharing = float(transaction.get("device_customer_count", transaction.get("device_sharing", 1)) or 1)
        fallback_ml = min(100.0, max(0.0, 20.0 + (velocity * 3.5) + (failed * 10.0) + (15.0 if amount > 20000 else 0.0)))
        fallback_anomaly = min(100.0, max(0.0, 15.0 + (velocity * 2.8) + (device_sharing * 8.0)))
        return {"ml_score": round(fallback_ml, 2), "anomaly_score": round(fallback_anomaly, 2)}
    features = to_features(transaction)
    probability = float(fraud_model.predict_proba(features)[0, 1]) * 100
    raw_anomaly = float(-anomaly_model.score_samples(features)[0])
    normalized_anomaly = max(0.0, min(100.0, (raw_anomaly - 0.35) / 0.5 * 100)) if raw_anomaly > 0.35 else max(0.0, min(100.0, raw_anomaly * 100))
    return {"ml_score": round(probability, 2), "anomaly_score": round(normalized_anomaly, 2)}


if __name__ == "__main__":
    print(predict({"amount": 12840, "transaction_velocity": 14, "failed_attempts": 3, "device_customer_count": 6}))
