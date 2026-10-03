"""Feature preparation is separate from inference and supports raw/processed schemas."""
import math
import pandas as pd
from ml.training import FEATURE_COLUMNS, CHANNELS

def build_features(transactions: pd.DataFrame) -> pd.DataFrame:
    df=transactions.copy(); amount_col="amount" if "amount" in df else "amount_bdt"; df["amount"]=df[amount_col].astype(float); df["amount_log"]=df["amount"].clip(lower=1).map(math.log1p)
    df["sender_velocity"]=df.groupby("sender_wallet")["transaction_id"].transform("count") if "transaction_id" in df else 1
    df["receiver_velocity"]=df.groupby("receiver_wallet")["transaction_id"].transform("count") if "transaction_id" in df else 1
    df["hop_count"]=df.get("hop_count",1)
    if "is_cashout" in df: df["cashout_flag"]=df["is_cashout"].astype(int)
    else: df["cashout_flag"]=(df.get("transaction_type","")=="cashout").astype(int) if hasattr(df.get("transaction_type",""),"astype") else 0
    df["new_relationship"]=df.get("new_relationship",1); df["account_age_days"]=df.get("account_age_days",365)
    df["channel_code"]=df["channel"].map(CHANNELS).fillna(0) if "channel" in df else 0; df["merchant_flag"]=df.get("merchant_flag",0)
    return df[FEATURE_COLUMNS].fillna(0)
