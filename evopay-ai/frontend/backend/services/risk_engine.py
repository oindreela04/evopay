from __future__ import annotations

from math import ceil
from typing import Any

try:
    from ..ml.predict import predict as ml_predict
except (ImportError, ValueError):
    try:
        from ml.predict import predict as ml_predict
    except (ImportError, ValueError):
        ml_predict = None


def _clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def _number(transaction: dict[str, Any], key: str, default: float = 0) -> float:
    try:
        return float(transaction.get(key, default))
    except (TypeError, ValueError):
        return default


def calculate_ml_score(transaction: dict[str, Any], context: dict[str, Any] | None = None) -> int:
    transaction = transaction or {}
    context = context or {}
    if ml_predict is not None:
        try:
            preds = ml_predict({**context, **transaction})
            if "ml_score" in preds:
                return _clamp(preds["ml_score"])
        except Exception:
            pass
    amount_deviation = min(_number(transaction, "amount_deviation", context.get("amount_deviation", 0)), 3)
    failed_attempts = min(_number(transaction, "failed_attempts", context.get("failed_attempts", 0)), 5)
    velocity = min(_number(transaction, "transaction_velocity", context.get("transaction_velocity", 0)), 20)
    return _clamp(25 + amount_deviation * 15 + failed_attempts * 6 + velocity * 1.8)


def calculate_behavior_score(transaction: dict[str, Any], context: dict[str, Any] | None = None) -> int:
    transaction = transaction or {}
    context = context or {}
    historical_deviation = min(_number(transaction, "historical_spending_deviation", context.get("historical_spending_deviation", 0)), 3)
    location_change = 1 if transaction.get("location_change", context.get("location_change", False)) else 0
    merchant_frequency = min(_number(transaction, "merchant_frequency", context.get("merchant_frequency", 0)), 10)
    return _clamp(18 + historical_deviation * 18 + location_change * 18 + merchant_frequency * 2.2)


def calculate_anomaly_score(transaction: dict[str, Any], context: dict[str, Any] | None = None) -> int:
    transaction = transaction or {}
    context = context or {}
    if ml_predict is not None:
        try:
            preds = ml_predict({**context, **transaction})
            if "anomaly_score" in preds:
                return _clamp(preds["anomaly_score"])
        except Exception:
            pass
    velocity = min(_number(transaction, "transaction_velocity", context.get("transaction_velocity", 0)), 20)
    device_sharing = min(_number(transaction, "device_sharing", context.get("device_sharing", 0)), 10)
    failed_attempts = min(_number(transaction, "failed_attempts", context.get("failed_attempts", 0)), 5)
    return _clamp(22 + velocity * 2.2 + device_sharing * 4 + failed_attempts * 4)


def calculate_graph_score(transaction: dict[str, Any], context: dict[str, Any] | None = None) -> int:
    transaction = transaction or {}
    context = context or {}
    high_risk_entities = min(_number(transaction, "connected_high_risk_entities", context.get("connected_high_risk_entities", 0)), 10)
    device_sharing = min(_number(transaction, "device_sharing", context.get("device_sharing", 0)), 10)
    suspicious_relationships = min(_number(transaction, "suspicious_relationships", context.get("suspicious_relationships", 0)), 8)
    return _clamp(24 + high_risk_entities * 4 + device_sharing * 3 + suspicious_relationships * 3)


def calculate_final_risk(ml: float, behavior: float, anomaly: float, graph: float) -> int:
    return _clamp(ceil(0.35 * ml + 0.20 * anomaly + 0.20 * behavior + 0.25 * graph))


def classify_risk(risk_score: int) -> str:
    if risk_score <= 30:
        return "LOW"
    if risk_score <= 60:
        return "MEDIUM"
    if risk_score <= 80:
        return "HIGH"
    return "CRITICAL"


def recommended_action(risk_score: int) -> str:
    if risk_score <= 30:
        return "ALLOW"
    if risk_score <= 60:
        return "VERIFY"
    if risk_score <= 80:
        return "HOLD"
    return "BLOCK"


def explain_risk(transaction: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    transaction = transaction or {}
    context = context or {}
    base_risk = _number(transaction, "risk_score", 0)
    high_threat = base_risk >= 80 or str(transaction.get("status", "")).upper() == "BLOCKED"
    signals = {
        "transaction_velocity": _number(transaction, "transaction_velocity", context.get("transaction_velocity", 14 if high_threat else 3.2)),
        "amount_deviation": _number(transaction, "amount_deviation", context.get("amount_deviation", 2.4 if high_threat else 0.4)),
        "account_age_days": _number(transaction, "account_age_days", context.get("account_age_days", 21 if high_threat else 340)),
        "device_sharing": _number(transaction, "device_sharing", context.get("device_sharing", 4 if high_threat else 1)),
        "location_change": bool(transaction.get("location_change", context.get("location_change", high_threat))),
        "merchant_frequency": _number(transaction, "merchant_frequency", context.get("merchant_frequency", 8 if high_threat else 2)),
        "failed_attempts": _number(transaction, "failed_attempts", context.get("failed_attempts", 3 if high_threat else 0)),
        "historical_spending_deviation": _number(transaction, "historical_spending_deviation", context.get("historical_spending_deviation", 2.1 if high_threat else 0.3)),
        "connected_high_risk_entities": _number(transaction, "connected_high_risk_entities", context.get("connected_high_risk_entities", 6 if high_threat else 0)),
    }
    scores = {
        "ml_score": calculate_ml_score(transaction, signals),
        "behavior_score": calculate_behavior_score(transaction, signals),
        "anomaly_score": calculate_anomaly_score(transaction, signals),
        "graph_score": calculate_graph_score(transaction, signals),
    }
    risk_score = calculate_final_risk(scores["ml_score"], scores["behavior_score"], scores["anomaly_score"], scores["graph_score"])
    if base_risk >= 80:
        risk_score = max(risk_score, int(base_risk))
    reasons = []
    if signals["transaction_velocity"] >= 6:
        reasons.append("High transaction velocity")
    if signals["device_sharing"] >= 2:
        reasons.append("Device linked to multiple accounts")
    if signals["merchant_frequency"] >= 4:
        reasons.append("Suspicious merchant relationship")
    if signals["historical_spending_deviation"] >= 1.2:
        reasons.append("Behavior differs significantly from historical baseline")
    if signals["connected_high_risk_entities"] >= 2:
        reasons.append("Connected to high-risk network cluster")
    return {"risk_score": risk_score, "classification": classify_risk(risk_score), "signals": {**signals, **scores}, "reasons": reasons, "recommended_action": recommended_action(risk_score)}


def analyze_transaction(transaction: dict[str, Any]) -> dict[str, Any]:
    return explain_risk(transaction)
