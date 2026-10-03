"""Calibrated multiclass model: where does money go in the 30 minutes after it lands? (forward / cashout / other)"""
from pathlib import Path
import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from ml.features import FEATURE_COLUMNS

class NextMoveModel:
    labels = ("forward", "cashout", "other")
    def __init__(self, model=None): self.model = model; self.fitted = model is not None
    def fit(self, X, y):
        base = HistGradientBoostingClassifier(max_depth=4, learning_rate=.06, max_iter=200, l2_regularization=1.0, min_samples_leaf=40, random_state=43)
        self.model = CalibratedClassifierCV(base, method="sigmoid", cv=3).fit(X, y); self.fitted = True; return self
    def _require(self):
        if not self.fitted: raise RuntimeError("NextMoveModel is not trained; run python -m ml.train_fraud_model")
    def predict_proba(self, X): self._require(); return self.model.predict_proba(X)
    def save(self, path): self._require(); Path(path).parent.mkdir(parents=True, exist_ok=True); joblib.dump({"model": self.model, "feature_columns": FEATURE_COLUMNS}, path)
    @classmethod
    def load(cls, path):
        a = joblib.load(path); return cls(a["model"] if isinstance(a, dict) else a)
