"""Unsupervised behavioural-anomaly layer (Isolation Forest) trained on mostly-legitimate traffic."""
from pathlib import Path
import joblib, numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyModel:
    def __init__(self, model=None, ref=None): self.model, self.ref = model, ref
    def fit(self, X):
        self.model = IsolationForest(n_estimators=200, contamination="auto", random_state=42, n_jobs=-1).fit(X)
        self.ref = np.sort(-self.model.score_samples(X)); return self
    def raw(self, X): return -self.model.score_samples(X)
    def percentile(self, X):
        """0..1: share of training traffic that is LESS anomalous than this transaction."""
        return np.searchsorted(self.ref, self.raw(X)) / len(self.ref)
    def save(self, path): Path(path).parent.mkdir(parents=True, exist_ok=True); joblib.dump({"model": self.model, "ref": self.ref}, path)
    @classmethod
    def load(cls, path): a = joblib.load(path); return cls(a["model"], a["ref"])
