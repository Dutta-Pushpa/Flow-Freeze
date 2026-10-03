"""Inference facade that loads persisted models; it never trains or returns constants."""
from functools import lru_cache
from pathlib import Path
import json
import pandas as pd
from ml.features import build_features, FEATURE_COLUMNS
from ml.fraud_model import FraudModel
from ml.next_move_model import NextMoveModel
MODEL_DIR=Path("models")

def _row(payload):
    row=dict(payload); row["amount_bdt"]=row.pop("amount",row.get("amount_bdt",0)); return pd.DataFrame([row])
@lru_cache(maxsize=1)
def trained_models():
    fraud_path=MODEL_DIR/"fraud_model.joblib"; next_path=MODEL_DIR/"next_move_model.joblib"
    if not fraud_path.exists() or not next_path.exists(): raise RuntimeError("Persisted models missing; run python -m data_generator.generate_transactions && python -m ml.train_fraud_model")
    return FraudModel.load(fraud_path), NextMoveModel.load(next_path)
def predict_fraud(features):
    frame=features if isinstance(features,pd.DataFrame) else _row(features); X=build_features(frame); model,_=trained_models(); p=float(model.predict_proba(X)[0,1]); return {"fraud_probability":round(p,6),"risk_score":round(p*100,2),"prediction":int(p>=.5),"model":"RandomForestClassifier","feature_columns":FEATURE_COLUMNS,"features":X.iloc[0].to_dict()}
def predict_next_move(features):
    frame=features if isinstance(features,pd.DataFrame) else _row(features); X=build_features(frame); _,model=trained_models(); probs=model.predict_proba(X)[0]; result={label:0.0 for label in ("forward","cashout","other")}; result.update({str(label):round(float(prob),6) for label,prob in zip(model.model.classes_,probs)}); return {**result,"model":"RandomForestClassifier","feature_columns":FEATURE_COLUMNS}
def evaluate_experiment():
    path=Path("data/processed/evaluation.json")
    if not path.exists(): raise RuntimeError("Evaluation artifact missing; run python -m ml.train_fraud_model")
    return json.loads(path.read_text())
