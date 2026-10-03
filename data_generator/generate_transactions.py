"""Behavioural MFS simulator (synthetic, reproducible).

Why this is NOT circular: labels come from simulated *episodes* (account-takeover, scam, mule layering),
not from feature ranges. Fraud and legitimate behaviour deliberately overlap:
  * stealth fraud (normal amount / same device) -> hard false negatives
  * legitimate look-alikes (salary fan-out, big one-off payments, new phone, informal sellers, merchant bursts)
  * label noise (unreported fraud, mis-reported legitimate tx)
Every feature is computed from the *history before the transaction* (no future leakage), exactly as it would be
at serving time. next_action is the receiver's *observed* behaviour in the following 30 minutes.
"""
from __future__ import annotations
import bisect, heapq
from collections import defaultdict, deque
from pathlib import Path
import numpy as np
import pandas as pd
from .config import (SEED, WALLETS, TRANSACTIONS, DAYS, START, EPISODE_RATE, STEALTH_ATO, STEALTH_SCAM,
                     LABEL_MISS_RATE, LABEL_FALSE_RATE)

HOUR_W = np.array([1,1,1,1,1,2,4,7,9,10,10,10,9,9,9,9,10,11,12,12,11,8,5,3], float)
HOUR_P = HOUR_W / HOUR_W.sum()
DISTRICTS = ["Dhaka","Chattogram","Sylhet","Rajshahi","Khulna","Barishal","Rangpur","Mymensingh"]
NEXT_WINDOW_MIN = 30

def _clip_amt(x, lo=50, hi=80_000): return float(min(max(round(x / 10) * 10, lo), hi))

def generate_dataset(n=TRANSACTIONS, seed=SEED, days=DAYS, n_wallets=WALLETS):
    rng = np.random.default_rng(seed)
    ids = np.array([f"W{i:04d}" for i in range(1, n_wallets + 1)]); perm = rng.permutation(n_wallets)
    counts = {"merchant": int(n_wallets*.07), "agent": int(n_wallets*.03), "mule": int(n_wallets*.04), "seller": int(n_wallets*.06)}
    role = {}; pos = 0
    for r, c in counts.items():
        for i in perm[pos:pos+c]: role[ids[i]] = r
        pos += c
    for i in perm[pos:]: role[ids[i]] = "customer"
    by_role = {r: [w for w in ids if role[w] == r] for r in ["customer","merchant","agent","mule","seller"]}
    senders = np.array(by_role["customer"] + by_role["seller"])
    act = rng.lognormal(0, .8, len(senders)); act /= act.sum()
    mw = 1 / (np.arange(len(by_role["merchant"])) + 1) ** .8; mw /= mw.sum()
    age0, bal, scale, district = {}, {}, {}, {}
    for w in ids:
        r = role[w]
        age0[w] = (np.clip(rng.lognormal(np.log(380), .8), 10, 2500) if r == "customer" else
                   np.clip(rng.lognormal(np.log(600), .6), 90, 2500) if r == "merchant" else
                   rng.uniform(300, 2500) if r == "agent" else
                   (rng.uniform(3, 60) if rng.random() < .55 else np.clip(rng.lognormal(np.log(300), .8), 90, 2000)) if r == "mule" else
                   np.clip(rng.lognormal(np.log(250), .7), 30, 2500))
        bal[w] = float(round(rng.lognormal(np.log({"customer":5000,"merchant":40000,"agent":300000,"mule":3500,"seller":12000}[r]), .9)))
        scale[w] = float(np.clip(rng.lognormal(np.log(1500 if r == "seller" else 1100), .6), 150, 8000))
        district[w] = DISTRICTS[int(rng.integers(len(DISTRICTS)))]
    contacts = {w: list(rng.choice([s for s in senders if s != w], 5, replace=False)) for w in senders}
    recv_pool = np.array(by_role["customer"] + by_role["seller"] + by_role["mule"])
    start_ts = pd.Timestamp(START, tz="Asia/Dhaka")

    base_t = np.sort(rng.integers(0, days, n) * 1440 + rng.choice(24, n, p=HOUR_P) * 60 + rng.integers(0, 60, n)).astype(float)
    out_h = defaultdict(deque); in_h = defaultdict(deque); seen = set(); amt_sum = defaultdict(float); amt_cnt = defaultdict(int)
    rows, episodes, heap = [], [], []; seq = [0]

    def push(ts, **kw): seq[0] += 1; heapq.heappush(heap, (ts, seq[0], kw))
    def agent(): return str(rng.choice(by_role["agent"]))
    def gamma_delay(shape, sc, lo=1.0): return float(lo + rng.gamma(shape, sc))

    def emit(ts, s, r, amount, ttype, channel, device, fraud, scenario, profile, episode=""):
        for h, k in ((out_h[s], 0), (in_h[r], 0)):
            while h and h[0][0] < ts - 1440: h.popleft()
        in_s = in_h[s]
        while in_s and in_s[0][0] < ts - 1440: in_s.popleft()
        sv = sum(1 for e in out_h[s] if e[0] >= ts - 60); rv = sum(1 for e in in_h[r] if e[0] >= ts - 60)
        fo = len({e[1] for e in out_h[s]}); fi = len({e[1] for e in in_h[r]})
        recent_in = sum(e[2] for e in in_s if e[0] >= ts - 15)
        avg = amt_sum[s] / amt_cnt[s] if amt_cnt[s] >= 3 else scale.get(s, 1000.0)
        rows.append({"transaction_id": f"TX-{len(rows):06d}", "episode_id": episode, "scenario": scenario, "legit_profile": profile,
            "ts_min": ts, "sender_wallet": s, "receiver_wallet": r, "amount_bdt": amount, "transaction_type": ttype, "status": "completed",
            "channel": channel, "sender_velocity": sv, "receiver_velocity": rv, "sender_fan_out_24h": fo, "receiver_fan_in_24h": fi,
            "new_relationship": int((s, r) not in seen), "rapid_forwarding": int(recent_in >= .6 * amount),
            "amount_vs_sender_avg": round(amount / max(avg, 1.0), 4), "hour": int((ts % 1440) // 60),
            "account_age_days": int(age0[s] + ts / 1440), "receiver_age_days": int(age0[r] + ts / 1440),
            "device_changed": int(device), "merchant_flag": int(role[r] == "merchant"), "cashout_flag": int(ttype == "cashout"),
            "true_fraud": int(fraud)})
        seen.add((s, r)); out_h[s].append((ts, r, amount)); in_h[r].append((ts, s, amount)); amt_sum[s] += amount; amt_cnt[s] += 1

    def start_episode(t):
        kind = str(rng.choice(["ato", "scam", "layering"], p=[.40, .35, .25]))
        ep = f"EP-{len(episodes):05d}"; victim = str(rng.choice(senders, p=act))
        ato_like = kind == "ato" or (kind == "layering" and rng.random() < .5)
        stealth = rng.random() < (STEALTH_ATO if ato_like else STEALTH_SCAM)
        mult = rng.uniform(.8, 1.8) if stealth else (rng.uniform(2.5, 9) if ato_like else rng.uniform(1.5, 6))
        amount = _clip_amt(scale[victim] * mult, 500)
        device = rng.random() < ((.30 if stealth else .85) if ato_like else .04)
        mule = rng.random() < .75 or kind == "layering"
        recv = str(rng.choice(by_role["mule"])) if mule else str(rng.choice(by_role["customer"]))
        if recv == victim: recv = str(rng.choice(by_role["mule"]))
        n0 = len(rows)
        emit(t, victim, recv, amount, "transfer", str(rng.choice(["app", "ussd"], p=[.6, .4])), device, 1, kind, "fraud", ep)
        first_id = rows[n0]["transaction_id"]; d1 = np.nan; frac = 0.0
        r = rng.random(); move = "forward" if kind == "layering" else ("none" if r < .15 else "cashout" if r < .70 else "forward")
        if move != "none":
            d1 = gamma_delay(2, 3.0); frac = float(rng.uniform(.6, 1.0)); a1 = _clip_amt(amount * frac)
            if move == "cashout": push(t + d1, s=recv, r=agent(), a=a1, tt="cashout", ch="agent", dev=0, fr=1, sc=kind, pr="fraud", ep=ep)
            else:
                m2 = str(rng.choice(by_role["mule"]))
                push(t + d1, s=recv, r=m2, a=a1, tt="transfer", ch="app", dev=0, fr=1, sc=kind, pr="fraud", ep=ep)
                push(t + d1 + gamma_delay(2, 3.0), s=m2, r=agent(), a=_clip_amt(a1 * rng.uniform(.85, 1)), tt="cashout", ch="agent", dev=0, fr=1, sc=kind, pr="fraud", ep=ep)
        episodes.append({"episode_id": ep, "scenario": kind, "victim_wallet": victim, "mule_wallet": recv, "t0_min": t, "first_fraud_tx_id": first_id,
                         "amount_bdt": amount, "first_move_delay_min": d1, "moved_fraction": frac, "mule_own_balance_bdt": bal[recv]})

    def legit_followups(t, recv, amount):
        r = role[recv]
        if r not in ("customer", "seller"): return
        pc, pf = (.07, .04) if r == "customer" else (.30, .12); u = rng.random()
        if u < pc: push(t + gamma_delay(2, 5.0), s=recv, r=agent(), a=_clip_amt(amount * rng.uniform(.5, 1)), tt="cashout", ch="agent", dev=0, fr=0, sc="normal", pr="normal", ep="")
        elif u < pc + pf: push(t + gamma_delay(2, 5.0), s=recv, r=str(rng.choice(contacts.get(recv, [recv]))), a=_clip_amt(amount * rng.uniform(.4, .9)), tt="transfer", ch="app", dev=0, fr=0, sc="normal", pr="normal", ep="")

    def legit_event(t):
        s = str(rng.choice(senders, p=act)); u = rng.random(); sc = scale[s]; ch2 = str(rng.choice(["app", "ussd"], p=[.7, .3]))
        if u < .32:
            m = str(rng.choice(by_role["merchant"], p=mw)); emit(t, s, m, _clip_amt(sc * rng.lognormal(0, .5)), "transfer", ch2, rng.random() < .02, 0, "normal", "merchant")
        elif u < .44:
            emit(t, s, agent(), _clip_amt(sc * rng.lognormal(.4, .5)), "cashout", str(rng.choice(["agent", "ussd"], p=[.8, .2])), rng.random() < .02, 0, "normal", "normal")
        elif u < .80:
            r = str(rng.choice(contacts[s])); a = _clip_amt(sc * rng.lognormal(0, .6))
            emit(t, s, r, a, "transfer", ch2, rng.random() < .02, 0, "normal", "normal"); legit_followups(t, r, a)
        elif u < .90:
            pool = by_role["seller"] if rng.random() < .25 else recv_pool; r = str(rng.choice(pool))
            if r == s: r = str(rng.choice(by_role["seller"]))
            a = _clip_amt(sc * rng.lognormal(0, .6)); emit(t, s, r, a, "transfer", ch2, rng.random() < .02, 0, "normal", "normal"); legit_followups(t, r, a)
        else:  # legitimate look-alikes that overlap with fraud
            k = rng.random(); prof = "unusual"
            if k < .35:
                r = str(rng.choice(recv_pool)); a = _clip_amt(sc * rng.uniform(3, 9)); emit(t, s, r, a, "transfer", ch2, rng.random() < .05, 0, "unusual_oneoff", prof); legit_followups(t, r, a)
            elif k < .65:
                r = str(rng.choice(contacts[s])); emit(t, s, r, _clip_amt(sc * rng.lognormal(0, .5)), "transfer", ch2, 1, 0, "unusual_new_device", prof)
            else:
                for j in range(int(rng.integers(4, 8))):
                    push(t + j * float(rng.uniform(.5, 2.5)), s=s, r=str(rng.choice(recv_pool)), a=_clip_amt(sc * rng.uniform(.8, 2.2)), tt="transfer", ch=ch2, dev=0, fr=0, sc="unusual_fanout", pr=prof, ep="")

    i = 0
    while len(rows) < n and (i < len(base_t) or heap):
        if heap and (i >= len(base_t) or heap[0][0] <= base_t[i]):
            ts, _, e = heapq.heappop(heap); emit(ts, e["s"], e["r"], e["a"], e["tt"], e["ch"], e["dev"], e["fr"], e["sc"], e["pr"], e["ep"])
        else:
            t = float(base_t[i]); i += 1
            start_episode(t) if rng.random() < EPISODE_RATE else legit_event(t)

    df = pd.DataFrame(rows[:n]); last = df.ts_min.max() if len(df) else 0
    out_idx = defaultdict(list)
    for s, ts, tt in zip(df.sender_wallet, df.ts_min, df.transaction_type): out_idx[s].append((ts, tt))
    na = []
    for r, ts in zip(df.receiver_wallet, df.ts_min):
        lst = out_idx.get(r, []); k = bisect.bisect_right(lst, (ts, "~")); nxt = [e for e in lst[k:k + 3] if e[0] <= ts + NEXT_WINDOW_MIN]
        na.append("other" if not nxt else ("cashout" if nxt[0][1] == "cashout" else "forward"))
    df["next_action"] = na
    rng2 = np.random.default_rng(seed + 1); u = rng2.random(len(df)) if len(df) else np.array([])
    df["is_fraud"] = np.where(df.true_fraud == 1, (u >= LABEL_MISS_RATE).astype(int), (u < LABEL_FALSE_RATE).astype(int)) if len(df) else []
    df["timestamp"] = [start_ts + pd.Timedelta(minutes=float(m)) for m in df.ts_min]
    eps = pd.DataFrame(episodes, columns=["episode_id","scenario","victim_wallet","mule_wallet","t0_min","first_fraud_tx_id","amount_bdt","first_move_delay_min","moved_fraction","mule_own_balance_bdt"])
    eps = eps[eps.first_fraud_tx_id.isin(set(df.transaction_id))] if len(df) else eps
    wallets = pd.DataFrame({"wallet_id": ids, "wallet_type": [role[w] if role[w] != "mule" else "customer" for w in ids], "synthetic_role": [role[w] for w in ids],
                            "balance_bdt": [bal[w] for w in ids], "district": [district[w] for w in ids], "account_age_days": [int(age0[w]) for w in ids]})
    return df, wallets, eps

def generate_transactions(n=TRANSACTIONS, seed=SEED): return generate_dataset(n, seed)[0]

def build_processed_features(raw):
    df = raw.copy(); df["timestamp"] = pd.to_datetime(df["timestamp"]); df["hour"] = df["timestamp"].dt.hour
    df["is_cashout"] = (df["transaction_type"] == "cashout").astype(int); return df

if __name__ == "__main__":
    raw, wallets, eps = generate_dataset(); processed = build_processed_features(raw)
    for p in ("data/raw", "data/processed", "data/synthetic"): Path(p).mkdir(parents=True, exist_ok=True)
    raw.to_csv("data/raw/generated_transactions.csv", index=False); processed.to_csv("data/processed/generated_transactions_features.csv", index=False)
    wallets.to_csv("data/synthetic/wallets.csv", index=False); eps.to_csv("data/processed/episodes.csv", index=False)
    print(f"{len(raw)} tx | fraud(true) {raw.true_fraud.mean():.3%} | fraud(label) {raw.is_fraud.mean():.3%} | episodes {len(eps)} | wallets {len(wallets)}")
