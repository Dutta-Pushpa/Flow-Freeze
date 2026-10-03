"""Reproducible synthetic experiment used by the API, notebooks, and dashboard."""
from __future__ import annotations
from functools import lru_cache
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

FEATURE_COLUMNS = ["amount_log", "sender_velocity", "receiver_velocity", "hop_count", "cashout_flag", "new_relationship", "account_age_days", "channel_code", "merchant_flag"]
CHANNELS = {"app": 0, "ussd": 1, "agent": 2}
SCENARIOS = [
    ("account_takeover", 1, 2, 3, 0, 1, 4, "ussd", 0, "fraud"),
    ("money_mule", 1, 5, 7, 1, 1, 19, "app", 0, "fraud"),
    ("scam_transaction", 1, 3, 4, 1, 1, 120, "app", 0, "fraud"),
    ("legitimate_merchant", 0, 2, 3, 0, 0, 920, "app", 1, "legit"),
    ("legitimate_unusual", 0, 2, 2, 0, 1, 640, "agent", 0, "legit"),
]

def make_experiment_dataset(repeats: int = 24) -> pd.DataFrame:
    rows = []
    for scenario, label, velocity, receiver_velocity, hop, cashout, age, channel, merchant, _ in SCENARIOS:
        for i in range(repeats):
            jitter = ((i * 7) % 9 - 4) / 10
            amount = max(300, (1800 if label else 1200) * (1 + jitter / 5) + i * (420 if label else 90))
            rows.append({"scenario": scenario, "label": label, "amount": amount, "amount_log": np.log1p(amount), "sender_velocity": max(1, velocity + (i % 3)), "receiver_velocity": max(1, receiver_velocity + ((i + 1) % 3)), "hop_count": hop + (i % 2), "cashout_flag": cashout if i % 4 else int(label), "new_relationship": int(bool((i + 2) % 5 < 3)) if not label else 1, "account_age_days": max(2, age + (i % 17 - 8)), "channel": channel if i % 6 else ("agent" if label else "ussd"), "channel_code": CHANNELS[channel], "merchant_flag": merchant, "customer_type": "merchant" if merchant else "personal", "account_segment": "new" if age < 90 else "old", "y_true": label})
    return pd.DataFrame(rows)

def feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        out = pd.DataFrame(df)
        if len(out.columns) <= len(FEATURE_COLUMNS): out.columns = FEATURE_COLUMNS[:len(out.columns)]
    else:
        out = df.copy()
    if "amount_log" not in out: out["amount_log"] = np.log1p(out["amount"].clip(lower=1))
    if "channel_code" not in out: out["channel_code"] = out["channel"].map(CHANNELS).fillna(0) if "channel" in out else 0
    for col in FEATURE_COLUMNS:
        if col not in out: out[col] = 0
    return out[FEATURE_COLUMNS].astype(float)

@lru_cache(maxsize=1)
def trained_models():
    data = make_experiment_dataset()
    X = feature_frame(data)
    fraud = HistGradientBoostingClassifier(max_iter=120, learning_rate=.08, max_leaf_nodes=12, random_state=42).fit(X, data.y_true)
    move = data.copy()
    move["next_move"] = np.select([move.cashout_flag.eq(1), move.sender_velocity.ge(4)], ["cashout", "forward"], default="other")
    next_move = HistGradientBoostingClassifier(max_iter=100, learning_rate=.08, max_leaf_nodes=10, random_state=43).fit(X, move.next_move)
    return fraud, next_move

def predict_fraud(features: dict | pd.DataFrame) -> dict:
    frame = features if isinstance(features, pd.DataFrame) else pd.DataFrame([features])
    model, _ = trained_models(); proba = float(model.predict_proba(feature_frame(frame))[0, 1])
    return {"risk_score": round(proba, 6), "prediction": int(proba >= .5), "model": "HistGradientBoostingClassifier", "features": feature_frame(frame).iloc[0].to_dict()}

def predict_next_move(features: dict | pd.DataFrame) -> dict:
    frame = features if isinstance(features, pd.DataFrame) else pd.DataFrame([features])
    _, model = trained_models(); probs = model.predict_proba(feature_frame(frame))[0]
    result = {label: round(float(prob), 6) for label, prob in zip(model.classes_, probs)}
    return {"forward": result.get("forward", 0.0), "cashout": result.get("cashout", 0.0), "other": result.get("other", 0.0), "model": "HistGradientBoostingClassifier"}

def evaluate_experiment() -> dict:
    data = make_experiment_dataset(); train, test = train_test_split(data, test_size=.3, random_state=42, stratify=data.y_true)
    model, _ = trained_models(); pred = model.predict(feature_frame(test)); truth = test.y_true.to_numpy()
    def metrics(y, p):
        tn, fp, fn, tp = confusion_matrix(y, p, labels=[0, 1]).ravel(); precision = tp / max(tp + fp, 1); recall = tp / max(tp + fn, 1); f1 = 2 * precision * recall / max(precision + recall, 1e-9)
        return {"precision": float(round(precision, 6)), "recall": float(round(recall, 6)), "f1": float(round(f1, 6)), "false_positives": int(fp), "false_negatives": int(fn), "support": int(len(y))}
    slices = {}
    for name, values in [("new_accounts", test.account_segment.eq("new")), ("old_accounts", test.account_segment.eq("old")), ("app", test.channel.eq("app")), ("ussd", test.channel.eq("ussd")), ("agent", test.channel.eq("agent")), ("merchant", test.customer_type.eq("merchant")), ("personal", test.customer_type.eq("personal"))]:
        subset = test.loc[values]
        slices[name] = metrics(subset.y_true, model.predict(feature_frame(subset))) if len(subset) else {"support": 0}
    baseline = (test.sender_velocity.ge(4) | test.cashout_flag.eq(1)).astype(int)
    return {"experiment": {"dataset": "make_experiment_dataset", "seed": 42, "train_rows": len(train), "test_rows": len(test), "scenario_count": 5, "scenarios": [s[0] for s in SCENARIOS]}, "baseline": metrics(truth, baseline), "flowfreeze": metrics(truth, pred), "slices": slices}

if __name__ == "__main__":
    import json
    print(json.dumps(evaluate_experiment()))
