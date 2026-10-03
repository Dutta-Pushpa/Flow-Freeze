import uuid
from .policies import policy

def recommend(balance, tainted_amount, cashout_probability, evidence, fraud_probability=None, alert=None, margin=0.0):
    ratio = tainted_amount / max(balance, 1); pol = policy("wallet", ratio, cashout_probability, alert)
    amount = min(balance, round(tainted_amount * (1 + margin)))
    conf = fraud_probability if fraud_probability is not None else cashout_probability
    return {"amount": amount, "scope": pol["scope"], "rationale": "; ".join(evidence), "confidence": round(float(conf), 4),
            "confidence_basis": "calibrated fraud probability" if fraud_probability is not None else "calibrated cash-out probability",
            "cashout_probability": round(float(cashout_probability), 4), "collateral_estimate": max(0, balance - amount),
            "requires_human_approval": True, "hold_max_hours": pol["hold_max_hours"], "customer_notice_required": pol["customer_notice_required"],
            "appeal_path": pol["appeal_path"], "caveat": "an intermediate wallet may belong to an innocent victim; review before any hold", "trace_id": f"ff-{uuid.uuid4().hex[:16]}"}
