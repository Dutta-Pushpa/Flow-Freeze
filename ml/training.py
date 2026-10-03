"""Inference facade that loads persisted models; it never trains or returns constants."""
from functools import lru_cache
from pathlib import Path
import json, uuid
import numpy as np, pandas as pd
from ml.features import build_features, FEATURE_COLUMNS
from ml.fraud_model import FraudModel
from ml.next_move_model import NextMoveModel
from ml.anomaly import AnomalyModel
from ml.explain import explain_prediction as _explain
MODEL_DIR = Path("models")

def _row(payload):
    row = dict(payload)
    if "amount_bdt" not in row: row["amount_bdt"] = row.pop("amount", row.pop("reported_amount", 0))   # accept amount | amount_bdt | reported_amount
    return pd.DataFrame([row])

@lru_cache(maxsize=1)
def trained_models():
    fp, npth = MODEL_DIR / "fraud_model.joblib", MODEL_DIR / "next_move_model.joblib"
    if not fp.exists() or not npth.exists(): raise RuntimeError("Persisted models missing; run python -m data_generator.generate_transactions && python -m ml.train_fraud_model")
    return FraudModel.load(fp), NextMoveModel.load(npth)

@lru_cache(maxsize=1)
def anomaly_model():
    p = MODEL_DIR / "anomaly_model.joblib"; return AnomalyModel.load(p) if p.exists() else None

def _frame(features): return features if isinstance(features, pd.DataFrame) else _row(features)

def predict_fraud(features):
    X = build_features(_frame(features)); model, _ = trained_models(); p = float(model.predict_proba(X)[0, 1]); amount = float(np.expm1(X["amount_log"].iloc[0]))
    an = anomaly_model(); alert = bool(p * amount >= model.threshold)
    out = {"fraud_probability": round(p, 6), "risk_score": round(p * 100, 2), "prediction": int(alert), "alert": alert, "expected_loss_bdt": round(p * amount, 2), "alert_threshold_bdt": round(model.threshold, 2),
           "calibrated": True, "model": model.meta.get("algorithm", "HistGradientBoosting + isotonic calibration"), "feature_columns": FEATURE_COLUMNS, "features": X.iloc[0].to_dict(), "trace_id": f"ff-{uuid.uuid4().hex[:16]}"}
    if an is not None: out["anomaly_percentile"] = round(float(an.percentile(X)[0]), 4)
    return out

def predict_next_move(features):
    X = build_features(_frame(features)); _, model = trained_models(); probs = model.predict_proba(X)[0]
    result = {label: 0.0 for label in ("forward", "cashout", "other")}; result.update({str(l): round(float(p), 6) for l, p in zip(model.model.classes_, probs)})
    return {**result, "model": "HistGradientBoosting + sigmoid calibration", "horizon_minutes": 30, "feature_columns": FEATURE_COLUMNS}

def explain_fraud(features, top=5):
    X = build_features(_frame(features)); model, _ = trained_models(); out = _explain(model, X, top)
    an = anomaly_model()
    if an is not None: out["anomaly_percentile"] = round(float(an.percentile(X)[0]), 4)
    return out

def evaluate_experiment():
    path = Path("data/processed/evaluation.json")
    if not path.exists(): raise RuntimeError("Evaluation artifact missing; run python -m ml.train_fraud_model")
    return json.loads(path.read_text())

def impact_summary():
    path = Path("data/processed/impact.json")
    if not path.exists(): raise RuntimeError("Impact artifact missing; run python -m ml.train_fraud_model")
    return json.loads(path.read_text())
