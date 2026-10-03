"""Generate reproducible, behaviorally distinct labeled MFS transactions."""
from pathlib import Path
import random
import pandas as pd
from .config import SEED, WALLETS, TRANSACTIONS

SCENARIO_WEIGHTS = [("normal", .55), ("account_takeover", .12), ("money_mule", .12), ("scam_transaction", .10), ("legitimate_merchant", .06), ("legitimate_unusual", .05)]

def generate_transactions(n=TRANSACTIONS, seed=SEED):
    rng = random.Random(seed); wallets = [f"W{i:03d}" for i in range(1, WALLETS + 1)]; scenarios, weights = zip(*SCENARIO_WEIGHTS)
    rows=[]
    for i in range(n):
        scenario = rng.choices(scenarios, weights=weights, k=1)[0]; sender, receiver = rng.sample(wallets, 2)
        fraud = int(scenario in {"account_takeover", "money_mule", "scam_transaction"})
        if scenario == "normal": amount=rng.choice([250,500,800,1200,2500]); velocity=rng.randint(1,3); receiver_velocity=rng.randint(1,3); new=0; rapid=0; age=rng.randint(180,1400); device=0; merchant=0; channel=rng.choice(["app","ussd"]); cashout=int(rng.random()<.12); next_action=rng.choices(["forward","cashout","other"],[.18,.12,.70])[0]
        elif scenario == "account_takeover": amount=rng.choice([8000,15000,20000,50000]); velocity=rng.randint(6,12); receiver_velocity=rng.randint(1,3); new=1; rapid=1; age=rng.randint(3,45); device=1; merchant=0; channel=rng.choice(["ussd","app"]); cashout=int(rng.random()<.30); next_action=rng.choices(["forward","cashout","other"],[.25,.62,.13])[0]
        elif scenario == "money_mule": amount=rng.choice([2500,5000,8000,15000]); velocity=rng.randint(7,15); receiver_velocity=rng.randint(5,12); new=1; rapid=1; age=rng.randint(10,80); device=0; merchant=0; channel=rng.choice(["app","agent"]); cashout=int(rng.random()<.65); next_action=rng.choices(["forward","cashout","other"],[.42,.48,.10])[0]
        elif scenario == "scam_transaction": amount=rng.choice([5000,10000,15000,30000]); velocity=rng.randint(2,6); receiver_velocity=rng.randint(2,5); new=1; rapid=int(rng.random()<.65); age=rng.randint(30,240); device=int(rng.random()<.35); merchant=0; channel=rng.choice(["app","ussd"]); cashout=int(rng.random()<.40); next_action=rng.choices(["forward","cashout","other"],[.18,.70,.12])[0]
        elif scenario == "legitimate_merchant": amount=rng.choice([800,1500,3000,7000,12000]); velocity=rng.randint(5,12); receiver_velocity=rng.randint(6,20); new=int(rng.random()<.15); rapid=int(rng.random()<.25); age=rng.randint(250,1800); device=0; merchant=1; channel="app"; cashout=int(rng.random()<.08); next_action=rng.choices(["forward","cashout","other"],[.12,.08,.80])[0]
        else: amount=rng.choice([4000,8000,15000]); velocity=rng.randint(2,6); receiver_velocity=rng.randint(1,4); new=1; rapid=int(rng.random()<.30); age=rng.randint(180,1400); device=int(rng.random()<.25); merchant=0; channel="agent"; cashout=int(rng.random()<.45); next_action=rng.choices(["forward","cashout","other"],[.16,.32,.52])[0]
        rows.append({"transaction_id":f"TX-{i:06d}","scenario_id":f"{scenario}-{i//4:04d}","scenario":scenario,"timestamp":pd.Timestamp("2026-10-01",tz="Asia/Dhaka")+pd.Timedelta(minutes=i*3),"sender_wallet":sender,"receiver_wallet":"CASHOUT" if cashout else receiver,"amount_bdt":amount,"transaction_type":"cashout" if cashout else "transfer","status":"completed","channel":channel,"sender_velocity":velocity,"receiver_velocity":receiver_velocity,"new_relationship":new,"rapid_forwarding":rapid,"account_age_days":age,"device_changed":device,"merchant_flag":merchant,"is_fraud":fraud,"next_action":next_action})
    return pd.DataFrame(rows)

def build_processed_features(raw):
    df=raw.copy(); df["timestamp"]=pd.to_datetime(df["timestamp"]); df["hour"]=df["timestamp"].dt.hour; df["is_cashout"]=(df["transaction_type"]=="cashout").astype(int); return df

if __name__ == "__main__":
    raw=generate_transactions(); processed=build_processed_features(raw); Path("data/raw").mkdir(parents=True,exist_ok=True); Path("data/processed").mkdir(parents=True,exist_ok=True); raw.to_csv("data/raw/generated_transactions.csv",index=False); processed.to_csv("data/processed/generated_transactions_features.csv",index=False)
