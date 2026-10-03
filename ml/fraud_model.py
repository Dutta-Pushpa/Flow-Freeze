"""Persistable supervised fraud model; inference is forbidden before fit/load."""
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from ml.features import FEATURE_COLUMNS
class FraudModel:
    def __init__(self, model=None): self.model=model; self.fitted=model is not None
    def fit(self,X,y): self.model=RandomForestClassifier(n_estimators=300,max_depth=12,min_samples_leaf=3,class_weight="balanced",random_state=42,n_jobs=-1).fit(X,y); self.fitted=True; return self
    def _require(self):
        if not self.fitted: raise RuntimeError("FraudModel is not trained; run python -m ml.train_fraud_model")
    def predict_proba(self,X): self._require(); return self.model.predict_proba(X)
    def predict(self,X): self._require(); return self.model.predict(X)
    def save(self,path): self._require(); Path(path).parent.mkdir(parents=True,exist_ok=True); joblib.dump({"model":self.model,"feature_columns":FEATURE_COLUMNS},path)
    @classmethod
    def load(cls,path):
        artifact=joblib.load(path); return cls(artifact["model"] if isinstance(artifact,dict) else artifact)
