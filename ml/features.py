"""Feature preparation is intentionally separate from inference."""
import pandas as pd
FEATURE_COLUMNS=["amount_log","sender_velocity","receiver_velocity","hop_count","cashout_flag","new_relationship"]
def build_features(transactions: pd.DataFrame) -> pd.DataFrame:
    df=transactions.copy(); df["amount_log"]=(df["amount"].clip(lower=1)).map(__import__("math").log1p); df["sender_velocity"]=df.groupby("sender_wallet")["transaction_id"].transform("count"); df["receiver_velocity"]=df.groupby("receiver_wallet")["transaction_id"].transform("count"); df["hop_count"]=df.get("hop_count",1); df["cashout_flag"]=df["is_cashout"].astype(int); df["new_relationship"]=1; return df[FEATURE_COLUMNS].fillna(0)
