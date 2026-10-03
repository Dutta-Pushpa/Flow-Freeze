"""Persistable multiclass next-action model trained from observed scenario outcomes."""
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
class NextMoveModel:
    labels=("forward","cashout","other")
    def __init__(self,model=None): self.model=model; self.fitted=model is not None
    def fit(self,X,y): self.model=RandomForestClassifier(n_estimators=300,max_depth=12,min_samples_leaf=3,class_weight="balanced",random_state=43,n_jobs=-1).fit(X,y); self.fitted=True; return self
    def _require(self):
        if not self.fitted: raise RuntimeError("NextMoveModel is not trained; run python -m ml.train_fraud_model")
    def predict_proba(self,X): self._require(); return self.model.predict_proba(X)
    def save(self,path): self._require(); Path(path).parent.mkdir(parents=True,exist_ok=True); joblib.dump({"model":self.model,"feature_columns":None},path)
    @classmethod
    def load(cls,path):
        artifact=joblib.load(path); return cls(artifact["model"] if isinstance(artifact,dict) else artifact)
