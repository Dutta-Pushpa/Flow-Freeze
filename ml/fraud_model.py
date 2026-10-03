"""Trained fraud classifier. Training data is deterministic synthetic behavior data."""
from ml.training import feature_frame, trained_models
class FraudModel:
    def __init__(self): self.model=trained_models()[0]; self.fitted=True
    def fit(self, X, y):
        from sklearn.ensemble import HistGradientBoostingClassifier
        self.model=HistGradientBoostingClassifier(max_iter=120, random_state=42).fit(X,y); return self
    def predict_proba(self, X): return self.model.predict_proba(feature_frame(X))
    def predict(self, X): return (self.predict_proba(X)[:,1]>=.5).astype(int)
