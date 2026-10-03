"""Behavioral feature engineering shared by training and inference."""
import math
import pandas as pd
FEATURE_COLUMNS=["amount_log","sender_velocity","receiver_velocity","cashout_flag","new_relationship","rapid_forwarding","amount_vs_sender_avg","hour","account_age_days","device_changed","merchant_flag","channel_code"]
CHANNELS={"app":0,"ussd":1,"agent":2}

def build_features(transactions: pd.DataFrame) -> pd.DataFrame:
    df=transactions.copy()
    amount_col="amount_bdt" if "amount_bdt" in df else "amount"
    df[amount_col]=pd.to_numeric(df[amount_col],errors="coerce").fillna(0)
    if "timestamp" in df:
        df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce"); df["hour"]=df.get("hour",df["timestamp"].dt.hour)
    else: df["hour"]=df.get("hour",12)
    df["amount_log"]=df.get("amount_log",df[amount_col].clip(lower=1).map(math.log1p))
    df["sender_velocity"]=df.get("sender_velocity",df.groupby("sender_wallet")["transaction_id"].transform("count") if "sender_wallet" in df and "transaction_id" in df else 1)
    df["receiver_velocity"]=df.get("receiver_velocity",df.groupby("receiver_wallet")["transaction_id"].transform("count") if "receiver_wallet" in df and "transaction_id" in df else 1)
    df["cashout_flag"]=df.get("cashout_flag",df.get("is_cashout",(df.get("transaction_type","")=="cashout").astype(int) if hasattr(df.get("transaction_type",""),"astype") else 0))
    df["new_relationship"]=df.get("new_relationship",1)
    if "rapid_forwarding" not in df:
        previous=df.groupby("sender_wallet")["timestamp"].shift(1) if "sender_wallet" in df and "timestamp" in df else pd.Series(0,index=df.index)
        df["rapid_forwarding"]=((df["timestamp"]-previous).dt.total_seconds().fillna(999999)<300).astype(int) if hasattr(previous,"dt") else 0
    avg=df.groupby("sender_wallet")[amount_col].transform("mean") if "sender_wallet" in df else df[amount_col]
    df["amount_vs_sender_avg"]=df.get("amount_vs_sender_avg",df[amount_col]/avg.clip(lower=1))
    df["account_age_days"]=df.get("account_age_days",365); df["device_changed"]=df.get("device_changed",0); df["merchant_flag"]=df.get("merchant_flag",0)
    channel=df.get("channel",pd.Series("app",index=df.index)); df["channel_code"]=df.get("channel_code",channel.map(lambda x: CHANNELS.get(str(x).lower(),0)))
    return df[FEATURE_COLUMNS].apply(pd.to_numeric,errors="coerce").fillna(0)
