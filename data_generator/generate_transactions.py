"""Generate reproducible synthetic MFS transactions."""
from pathlib import Path
import random
import pandas as pd
from .config import SEED, WALLETS, TRANSACTIONS

def generate_transactions(n=TRANSACTIONS, seed=SEED):
    rng=random.Random(seed); wallets=[f"W{i:03d}" for i in range(1,WALLETS+1)]
    rows=[]
    for i in range(n):
        sender,receiver=rng.sample(wallets,2); amount=rng.choice([500,800,1200,2500,5000,8000,15000])
        rows.append({"transaction_id":f"TX-{i:06d}","timestamp":pd.Timestamp("2026-10-01",tz="Asia/Dhaka")+pd.Timedelta(minutes=i*3),"sender_wallet":sender,"receiver_wallet":receiver,"amount":amount,"channel":rng.choice(["app","ussd","agent"]),"is_cashout":rng.random()<.12})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    out=Path("data/synthetic/transactions.csv"); out.parent.mkdir(parents=True,exist_ok=True); generate_transactions().to_csv(out,index=False)
