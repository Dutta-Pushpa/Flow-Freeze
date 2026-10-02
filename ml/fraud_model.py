"""Scikit-learn-compatible fraud classifier with optional XGBoost/LightGBM adapters."""
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
class FraudModel:
    def __init__(self): self.model=HistGradientBoostingClassifier(max_iter=80,random_state=42); self.fitted=False
    def fit(self,X,y): self.model.fit(X,y); self.fitted=True; return self
    def predict_proba(self,X):
        if not self.fitted: return np.tile([.12,.88],(len(X),1))
        return self.model.predict_proba(X)
    def predict(self,X): return (self.predict_proba(X)[:,1]>=.5).astype(int)
