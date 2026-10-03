"""Feature preparation shared by training and serving (no train/serve skew: every feature is produced by the
generator / upstream pipeline from history *before* the transaction; serving only fills documented defaults)."""
import math
import numpy as np
import pandas as pd

FEATURE_COLUMNS = ["amount_log", "sender_velocity", "receiver_velocity", "sender_fan_out_24h", "receiver_fan_in_24h",
                   "cashout_flag", "new_relationship", "rapid_forwarding", "amount_vs_sender_avg", "hour",
                   "account_age_days", "receiver_age_days", "device_changed", "merchant_flag", "channel_code"]
CHANNELS = {"app": 0, "ussd": 1, "agent": 2}
DEFAULTS = {"sender_velocity": 1, "receiver_velocity": 1, "sender_fan_out_24h": 1, "receiver_fan_in_24h": 1, "cashout_flag": 0,
            "new_relationship": 1, "rapid_forwarding": 0, "amount_vs_sender_avg": 1.0, "hour": 12, "account_age_days": 365,
            "receiver_age_days": 365, "device_changed": 0, "merchant_flag": 0}

def build_features(transactions: pd.DataFrame) -> pd.DataFrame:
    df = transactions.copy()
    amount = df["amount_bdt"] if "amount_bdt" in df else df["amount"] if "amount" in df else pd.Series(0.0, index=df.index)
    amount = pd.to_numeric(amount, errors="coerce").fillna(0).clip(lower=0)
    if "hour" not in df and "timestamp" in df: df["hour"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.hour
    if "cashout_flag" not in df and "transaction_type" in df: df["cashout_flag"] = (df["transaction_type"] == "cashout").astype(int)
    out = pd.DataFrame(index=df.index); out["amount_log"] = np.log1p(amount)
    for col, default in DEFAULTS.items(): out[col] = df[col] if col in df else default
    channel = df["channel"] if "channel" in df else pd.Series("app", index=df.index)
    out["channel_code"] = channel.map(lambda x: CHANNELS.get(str(x).lower(), 0))
    return out[FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0)
