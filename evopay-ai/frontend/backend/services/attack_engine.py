from __future__ import annotations

from copy import deepcopy
from typing import Any

ATTACK_TYPES = (
    "synthetic_identity", "account_takeover", "card_testing", "money_mule",
    "merchant_collusion", "behavioral_mimicry", "device_rotation", "refund_abuse",
    "velocity_attack", "composite_attack",
)

_BASE_PARAMETERS: dict[str, dict[str, float | int]] = {
    "synthetic_identity": {"accounts": 10, "devices": 4, "transaction_velocity": 2.1, "behavioral_similarity": .72},
    "account_takeover": {"accounts": 6, "devices": 3, "transaction_velocity": 3.2, "behavioral_similarity": .58},
    "card_testing": {"accounts": 4, "devices": 2, "transaction_velocity": 8.4, "behavioral_similarity": .36},
    "money_mule": {"accounts": 18, "devices": 7, "transaction_velocity": 4.7, "behavioral_similarity": .64},
    "merchant_collusion": {"accounts": 12, "devices": 5, "transaction_velocity": 3.8, "behavioral_similarity": .69},
    "behavioral_mimicry": {"accounts": 8, "devices": 3, "transaction_velocity": 2.8, "behavioral_similarity": .91},
    "device_rotation": {"accounts": 9, "devices": 11, "transaction_velocity": 5.1, "behavioral_similarity": .61},
    "refund_abuse": {"accounts": 7, "devices": 4, "transaction_velocity": 3.4, "behavioral_similarity": .55},
    "velocity_attack": {"accounts": 14, "devices": 5, "transaction_velocity": 9.2, "behavioral_similarity": .42},
    "composite_attack": {"accounts": 18, "devices": 7, "transaction_velocity": 6.8, "behavioral_similarity": .76},
}


def _clamp(value: float, low: float = 0, high: float = 100) -> int:
    return max(int(low), min(int(high), round(value)))


def _canonical(attack_type: str) -> str:
    normalized = attack_type.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized not in ATTACK_TYPES:
        raise ValueError(f"Unsupported attack type: {attack_type}")
    return normalized


def _score(parameters: dict[str, float | int], generation: int) -> dict[str, int | bool]:
    velocity = float(parameters["transaction_velocity"])
    similarity = float(parameters["behavioral_similarity"])
    coordination = min(float(parameters["accounts"]) / 20, 1)
    device_ratio = min(float(parameters["devices"]) / 12, 1)
    realism = _clamp(similarity * 58 + (1 - min(abs(velocity - 4) / 8, 1)) * 22 + coordination * 12 + device_ratio * 8)
    detection = _clamp(82 - similarity * 22 - generation * 4 + velocity * 1.2 + device_ratio * 8)
    evasion = detection < 45
    return {"attack_score": realism, "detection_probability": detection, "evasion_success": evasion}


def generate_attack(attack_type: str = "synthetic_identity", generation: int = 1) -> dict[str, Any]:
    canonical = _canonical(attack_type)
    generation = max(1, int(generation))
    parameters = deepcopy(_BASE_PARAMETERS[canonical])
    parameters["accounts"] = int(parameters["accounts"]) + (generation - 1) * 2
    parameters["devices"] = int(parameters["devices"]) + (generation - 1)
    parameters["transaction_velocity"] = round(float(parameters["transaction_velocity"]) + (generation - 1) * .35, 2)
    parameters["behavioral_similarity"] = round(min(.98, float(parameters["behavioral_similarity"]) + (generation - 1) * .04), 2)
    return {"attack_type": canonical, "generation": generation, **parameters, **_score(parameters, generation)}


def evolve_attack(attack: dict[str, Any]) -> dict[str, Any]:
    evolved = deepcopy(attack)
    generation = int(attack.get("generation", 1)) + 1
    parameters = {key: attack[key] for key in ("accounts", "devices", "transaction_velocity", "behavioral_similarity")}
    parameters["behavioral_similarity"] = round(min(.99, float(parameters["behavioral_similarity"]) + .04), 2)
    parameters["transaction_velocity"] = round(float(parameters["transaction_velocity"]) * 1.08, 2)
    parameters["accounts"] = int(parameters["accounts"]) + 2
    parameters["devices"] = int(parameters["devices"]) + 1
    evolved.update({"generation": generation, **parameters, **_score(parameters, generation)})
    return evolved


def attack_type_parameters(attack_type: str) -> dict[str, float | int]:
    return deepcopy(_BASE_PARAMETERS[_canonical(attack_type)])
