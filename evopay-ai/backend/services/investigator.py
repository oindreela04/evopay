from __future__ import annotations

from typing import Any

from .risk_engine import analyze_transaction


def _attack_type(transaction: dict[str, Any], network: dict[str, Any]) -> str:
    relationships = network.get("suspicious_relationships", network.get("relationships", []))
    relationship_count = len(relationships) if isinstance(relationships, list) else int(network.get("suspicious_relationship_count", 0) or 0)
    device_sharing = float(transaction.get("device_sharing", network.get("device_sharing", 0)) or 0)
    velocity = float(transaction.get("transaction_velocity", 0) or 0)
    if relationship_count >= 3 and device_sharing >= 2:
        return "Money mule network"
    if velocity >= 8:
        return "Velocity attack"
    if device_sharing >= 2:
        return "Device rotation"
    return "Composite payment fraud"


def investigate_transaction(transaction: dict[str, Any], network: dict[str, Any] | None = None) -> dict[str, Any]:
    transaction = transaction or {}
    network = network or {}
    risk = analyze_transaction({**transaction, **network})
    signals = risk["signals"]
    evidence = list(risk["reasons"])
    if not evidence:
        evidence = ["No material anomaly exceeded the current policy thresholds"]
    finding = {
        "LOW": "Transaction behavior is consistent with the established payment baseline.",
        "MEDIUM": "Transaction shows signals that warrant step-up verification.",
        "HIGH": "Transaction is likely part of a coordinated payment-fraud attempt.",
        "CRITICAL": "Transaction is likely part of a coordinated mule-network attack.",
    }[risk["classification"]]
    return {
        "finding": finding,
        "evidence": evidence,
        "risk": risk["classification"].title(),
        "attack_type": _attack_type(transaction, network),
        "recommended_action": risk["recommended_action"],
        "risk_score": risk["risk_score"],
        "signals": signals,
        "analysis_mode": "deterministic_local",
    }
