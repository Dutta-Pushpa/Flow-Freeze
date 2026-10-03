"""Exact Shapley-value attribution (no external SHAP dependency).

phi_j = sum over coalitions S (not containing j) of |S|!(d-|S|-1)!/d! * [v(S+j) - v(S)], where v(S) is the model's
calibrated fraud probability with features in S taken from the transaction and the rest from a *typical legitimate
transaction* (median of legitimate training rows). Features equal to the baseline contribute exactly 0, so the
enumeration only runs over the features that actually differ (<= 2^15 model calls, typically far fewer).
Additivity holds: sum(phi) = P(fraud | tx) - P(fraud | typical legitimate tx).
"""
from itertools import combinations
from math import factorial
import numpy as np

TEXT = {
    "amount_log": "unusually large amount", "sender_velocity": "many outgoing transfers in the last hour", "receiver_velocity": "receiver got many transfers in the last hour",
    "sender_fan_out_24h": "sender paid many different people in 24h", "receiver_fan_in_24h": "receiver collected from many different senders in 24h",
    "cashout_flag": "transaction is a cash-out", "new_relationship": "first ever transfer between these two wallets", "rapid_forwarding": "sender is forwarding money it just received",
    "amount_vs_sender_avg": "amount far above the sender's normal", "hour": "unusual hour of day", "account_age_days": "very new sender account",
    "receiver_age_days": "very new receiver account", "device_changed": "sender used a new device", "merchant_flag": "receiver is a known merchant", "channel_code": "channel used"}

def shapley(predict, x, baseline):
    x = np.asarray(x, float); b = np.asarray(baseline, float); d = len(x)
    active = [j for j in range(d) if x[j] != b[j]]; phi = np.zeros(d); k = len(active)
    if k == 0: return phi, float(predict(b[None])[0]), float(predict(b[None])[0])
    masks = np.array([[(m >> i) & 1 for i in range(k)] for m in range(2 ** k)], bool)
    X = np.tile(b, (2 ** k, 1)); X[:, active] = np.where(masks, x[active], b[active]); v = predict(X)
    w = [factorial(s) * factorial(k - s - 1) / factorial(k) for s in range(k)]; size = masks.sum(1)
    for pos, j in enumerate(active):
        idx = np.where(~masks[:, pos])[0]; phi[j] = float(np.sum([w[size[i]] * (v[i | (1 << pos)] - v[i]) for i in idx]))
    return phi, float(v[-1]), float(v[0])

def explain_prediction(model, row, top=5):
    """row: single-row DataFrame of FEATURE_COLUMNS. Returns ranked, human-readable drivers with signed contributions."""
    cols = list(row.columns); b = np.array([model.baseline[c] for c in cols], float)
    phi, p, p0 = shapley(lambda A: model.predict_proba(__import__("pandas").DataFrame(A, columns=cols))[:, 1], row.iloc[0].to_numpy(float), b)
    order = np.argsort(-np.abs(phi))[:top]; factors = []
    for j in order:
        if abs(phi[j]) < 1e-4: continue
        c = cols[j]; factors.append({"feature": c, "value": float(row.iloc[0][c]), "contribution": round(float(phi[j]), 4), "direction": "raises risk" if phi[j] > 0 else "lowers risk", "text": TEXT.get(c, c)})
    return {"fraud_probability": round(p, 4), "baseline_probability": round(p0, 4), "factors": factors, "method": "exact_shapley_values",
            "free_form_llm_used": False, "evidence": [(f"Model driver: {f['text']} (+{f['contribution'] * 100:.1f} pts of risk)" if f["contribution"] > 0 else f"Model driver: {f['feature']}={f['value']:g} points toward legitimate ({f['contribution'] * 100:.1f} pts)") for f in factors]}
