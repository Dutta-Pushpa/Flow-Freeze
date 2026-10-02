"""Generate reproducible synthetic MFS transactions and processed features."""
from pathlib import Path
import math
import random
import pandas as pd
from .config import SEED, WALLETS, TRANSACTIONS

def generate_transactions(n=TRANSACTIONS, seed=SEED):
    rng = random.Random(seed)
    wallets = [f"W{i:03d}" for i in range(1, WALLETS + 1)]
    rows = []
    for i in range(n):
        sender, receiver = rng.sample(wallets, 2)
        amount = rng.choice([500, 800, 1200, 2500, 5000, 8000, 15000])
        cashout = rng.random() < 0.12
        rows.append({"transaction_id": f"TX-{i:06d}", "timestamp": pd.Timestamp("2026-10-01", tz="Asia/Dhaka") + pd.Timedelta(minutes=i * 3), "sender_wallet": sender, "receiver_wallet": "CASHOUT" if cashout else receiver, "amount_bdt": amount, "transaction_type": "cashout" if cashout else "transfer", "status": "completed"})
    return pd.DataFrame(rows)

def build_processed_features(raw):
    df = raw.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["is_cashout"] = (df["transaction_type"] == "cashout").astype(int)
    df["amount_log"] = df["amount_bdt"].map(lambda value: round(math.log1p(value), 6))
    return df

if __name__ == "__main__":
    raw = generate_transactions()
    processed = build_processed_features(raw)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    raw.to_csv("data/raw/generated_transactions.csv", index=False)
    processed.to_csv("data/processed/generated_transactions_features.csv", index=False)
