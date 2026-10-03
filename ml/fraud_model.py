"""Calibrated gradient-boosting fraud model. Inference is forbidden before fit/load."""
from datetime import datetime, timezone
from pathlib import Path
import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from ml.features import FEATURE_COLUMNS

class FraudModel:
    def __init__(self, model=None, baseline=None, threshold=0.5, meta=None):
        self.model, self.baseline, self.threshold, self.meta = model, baseline, threshold, meta or {}; self.fitted = model is not None
    def fit(self, X, y):
        base = HistGradientBoostingClassifier(max_depth=5, learning_rate=.06, max_iter=250, l2_regularization=1.0, min_samples_leaf=30, random_state=42)
        self.model = CalibratedClassifierCV(base, method="isotonic", cv=3).fit(X, y)   # probabilities are calibrated, not raw scores
        self.baseline = X[y == 0].median().to_dict(); self.fitted = True
        self.meta = {"trained_at": datetime.now(timezone.utc).isoformat(), "algorithm": "HistGradientBoosting + isotonic calibration"}; return self
    def _require(self):
        if not self.fitted: raise RuntimeError("FraudModel is not trained; run python -m ml.train_fraud_model")
    def predict_proba(self, X): self._require(); return self.model.predict_proba(X)
    def alert(self, X):
        """Expected-loss alert rule: P(fraud) x amount >= threshold (threshold is in BDT, tuned on the validation window)."""
        import numpy as np
        self._require(); return (self.predict_proba(X)[:, 1] * np.expm1(X["amount_log"].to_numpy()) >= self.threshold).astype(int)
    predict = alert
    def save(self, path):
        self._require(); Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "feature_columns": FEATURE_COLUMNS, "baseline": self.baseline, "threshold": self.threshold, "meta": self.meta}, path)
    @classmethod
    def load(cls, path):
        a = joblib.load(path)
        if not isinstance(a, dict): return cls(a)
        if a.get("feature_columns") != FEATURE_COLUMNS: raise RuntimeError("Model artifact was trained with different features; retrain.")
        return cls(a["model"], a.get("baseline"), a.get("threshold", .5), a.get("meta"))
