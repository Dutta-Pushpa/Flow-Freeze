"""Honest baselines the ML model must beat: a hand-written rule engine and logistic regression."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def rule_flags(X):
    """Typical fixed rules an MFS ops team would run today (binary alerts, no probability)."""
    amount = np.expm1(X["amount_log"])
    r = ((amount >= 10_000) & (X["new_relationship"] == 1)) | ((X["device_changed"] == 1) & (X["amount_vs_sender_avg"] >= 3)) \
        | ((X["rapid_forwarding"] == 1) & (X["sender_velocity"] >= 5))
    return r.astype(int)

def fit_logistic(X, y):
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)).fit(X, y)
