"""Deterministic synthetic Indian-style payment dataset generator."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ATTACK_TYPES = ("normal", "synthetic_identity", "account_takeover", "card_testing", "money_mule", "merchant_collusion", "behavioral_mimicry", "device_rotation", "refund_abuse", "velocity_attack")
LOCATIONS = ("Kolkata", "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai")
METHODS = ("UPI", "Card", "Wallet", "Net Banking")
FEATURE_COLUMNS = ("amount", "account_age_days", "transaction_velocity", "failed_attempts", "device_changes", "merchant_frequency", "distance_from_previous_transaction", "average_customer_amount", "amount_deviation", "hour", "day_of_week", "customer_transaction_count", "device_customer_count", "merchant_customer_count")


def generate_dataset(rows: int = 100_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-01", periods=rows, freq="7min")
    labels = rng.choice(ATTACK_TYPES, rows, p=[.822, .025, .02, .025, .02, .015, .018, .015, .02, .02])
    is_fraud = labels != "normal"
    account_age = np.where(is_fraud, rng.integers(7, 900, rows), rng.integers(90, 2400, rows))
    velocity = np.where(is_fraud, rng.gamma(2.8, 2.2, rows), rng.gamma(2.1, 1.2, rows))
    failed = np.where(is_fraud, rng.poisson(1.7, rows), rng.poisson(.25, rows))
    device_changes = np.where(is_fraud, rng.poisson(1.4, rows), rng.poisson(.18, rows))
    merchant_frequency = np.where(is_fraud, rng.gamma(2.4, 2.1, rows), rng.gamma(2.2, 1.4, rows))
    average_amount = rng.lognormal(7.4, .65, rows)
    amount = np.where(is_fraud, average_amount * rng.lognormal(.55, .65, rows), average_amount * rng.lognormal(0, .35, rows))
    amount_deviation = np.abs(amount - average_amount) / np.maximum(average_amount, 1)
    distance = np.where(is_fraud, rng.gamma(2.3, 110, rows), rng.gamma(1.8, 24, rows))
    customer_count = rng.poisson(35, rows) + 1
    device_customers = np.where(is_fraud, rng.poisson(3, rows) + 2, rng.poisson(.8, rows) + 1)
    merchant_customers = np.where(is_fraud, rng.poisson(8, rows) + 3, rng.poisson(20, rows) + 3)
    hours = timestamps.hour.to_numpy()
    fraud_label = is_fraud.astype(int)
    return pd.DataFrame({
        "transaction_id": [f"SYN-{index:07d}" for index in range(rows)], "customer_id": [f"C-{value:05d}" for value in rng.integers(1, max(rows // 4, 2), rows)], "merchant_id": [f"M-{value:04d}" for value in rng.integers(1, 600, rows)], "device_id": [f"D-{value:05d}" for value in rng.integers(1, max(rows // 3, 2), rows)], "timestamp": timestamps.astype(str), "amount": np.round(amount).astype(int), "currency": "INR", "location": rng.choice(LOCATIONS, rows), "payment_method": rng.choice(METHODS, rows, p=[.54, .27, .12, .07]), "account_age_days": account_age, "transaction_velocity": np.round(velocity, 2), "failed_attempts": failed, "device_changes": device_changes, "merchant_frequency": np.round(merchant_frequency, 2), "distance_from_previous_transaction": np.round(distance, 2), "average_customer_amount": np.round(average_amount).astype(int), "amount_deviation": np.round(amount_deviation, 3), "hour": hours, "day_of_week": timestamps.dayofweek.to_numpy(), "customer_transaction_count": customer_count, "device_customer_count": device_customers, "merchant_customer_count": merchant_customers, "fraud_label": fraud_label, "attack_type": labels,
    })


def write_dataset(path: str | Path | None = None, rows: int = 100_000, seed: int = 42) -> Path:
    target = Path(path) if path else Path(__file__).parent / "data" / "synthetic_transactions.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    generate_dataset(rows, seed).to_csv(target, index=False)
    return target


if __name__ == "__main__":
    print(write_dataset())
