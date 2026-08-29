from __future__ import annotations

from typing import Any
import pandas as pd
try:
    from .data_generator import FEATURE_COLUMNS
except ImportError:
    from data_generator import FEATURE_COLUMNS

METHOD_CODES = {"UPI": 0, "Card": 1, "Wallet": 2, "Net Banking": 3}
LOCATION_CODES = {name: index for index, name in enumerate(("Kolkata", "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai"))}
MODEL_FEATURES = [*FEATURE_COLUMNS, "location_code", "payment_method_code"]


def to_features(data: pd.DataFrame | dict[str, Any]) -> pd.DataFrame:
    if isinstance(data, dict):
        frame = pd.DataFrame([data])
    else:
        frame = data.copy()
    if "device_customer_count" not in frame.columns and "device_sharing" in frame.columns:
        frame["device_customer_count"] = frame["device_sharing"]
    if "customer_transaction_count" not in frame.columns and "transaction_velocity" in frame.columns:
        frame["customer_transaction_count"] = frame["transaction_velocity"] * 3
    if "device_changes" not in frame.columns and "failed_attempts" in frame.columns:
        frame["device_changes"] = frame["failed_attempts"]
    for column in FEATURE_COLUMNS:
        if column not in frame.columns:
            frame[column] = 0
    if "location" in frame.columns:
        frame["location_code"] = frame["location"].map(LOCATION_CODES).fillna(-1)
    else:
        frame["location_code"] = -1
    if "payment_method" in frame.columns:
        frame["payment_method_code"] = frame["payment_method"].map(METHOD_CODES).fillna(-1)
    else:
        frame["payment_method_code"] = -1
    return frame[MODEL_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
