from data_generator.config import CASHOUT_HOLD_THRESHOLD, HOLD_MAX_HOURS
def policy(scope, taint_ratio, cashout_probability, alert=None):
    """Business rules live HERE, separate from the ML scores. Every branch still requires a human."""
    hold = {"hold_max_hours": HOLD_MAX_HOURS, "requires_human_approval": True, "customer_notice_required": True, "appeal_path": "analyst re-review within the hold window"}
    risky = alert is None or bool(alert)
    if risky and cashout_probability >= CASHOUT_HOLD_THRESHOLD and taint_ratio < .85: return {"scope": "wallet-level partial hold", **hold}
    if risky and cashout_probability >= CASHOUT_HOLD_THRESHOLD: return {"scope": "wallet-level hold", **hold}
    return {"scope": "monitor and request context", **{**hold, "customer_notice_required": False}}
