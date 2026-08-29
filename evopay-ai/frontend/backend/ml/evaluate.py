from __future__ import annotations
import json
from pathlib import Path
try:
    from .train import train
except ImportError:
    from train import train


def evaluate() -> dict:
    metrics_path = Path(__file__).parent / "models" / "metrics.json"
    if not metrics_path.exists():
        return train()
    return json.loads(metrics_path.read_text())


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
