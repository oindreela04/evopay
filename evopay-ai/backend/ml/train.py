from __future__ import annotations
import json
from pathlib import Path
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
try:
    from .data_generator import generate_dataset
    from .feature_engineering import to_features
except ImportError:
    from data_generator import generate_dataset
    from feature_engineering import to_features

ROOT = Path(__file__).parent
MODEL_DIR = ROOT / "models"


def train(rows: int = 100_000, seed: int = 42) -> dict:
    frame = generate_dataset(rows, seed)
    features = to_features(frame)
    labels = frame["fraud_label"]
    split = int(len(frame) * .8)
    validation_split = int(len(frame) * .9)
    model = HistGradientBoostingClassifier(max_iter=180, learning_rate=.08, max_leaf_nodes=31, random_state=seed, class_weight="balanced")
    model.fit(features.iloc[:split], labels.iloc[:split])
    
    test_features = features.iloc[validation_split:]
    truth = labels.iloc[validation_split:]
    probabilities = model.predict_proba(test_features)[:, 1]
    predictions = (probabilities >= .5).astype(int)

    anomaly = IsolationForest(n_estimators=120, contamination=.12, random_state=seed, n_jobs=-1)
    normal_features = features[labels == 0].sample(min(30_000, int((labels == 0).sum())), random_state=seed)
    anomaly.fit(normal_features)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "fraud_model.joblib")
    joblib.dump(anomaly, MODEL_DIR / "anomaly_model.joblib")

    cm = confusion_matrix(truth, predictions)
    tn, fp, fn, tp = cm.ravel()
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    metrics = {
        "model_version": "v1.0",
        "training_samples": split,
        "test_samples": len(truth),
        "accuracy": round(float(accuracy_score(truth, predictions)), 4),
        "precision": round(float(precision_score(truth, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(truth, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(truth, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(truth, probabilities)), 4),
        "pr_auc": round(float(average_precision_score(truth, probabilities)), 4),
        "false_positive_rate": round(fpr, 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
