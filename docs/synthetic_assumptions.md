# Synthetic-data assumptions (documented per the hackathon guideline)

Population: 800 wallets (customers 80%, merchants 7%, agents 3%, mule-capable 4%, informal sellers 6%), 20,000 transactions over a ≤21-day window. No real PII was used.
Parameters live in `data_generator/config.py`; reproducible with seed 42.

**Legitimate behaviour:** merchant payments (Zipf-distributed merchants), P2P to 5 stored contacts, cash-outs, transfers to new receivers (including informal sellers and, occasionally, mule-capable wallets), and 10% look-alikes: large one-off payments, new-phone logins, salary-day fan-out bursts.
**Fraud episodes (3% of base events):** account-takeover, scam, mule layering. 22% of takeovers and 35% of scams are *stealth* (normal amount, same device). The receiving wallet moves money onward after a gamma-distributed delay (mean ≈ 7 min): 55% cash-out, 30% forward to a second mule, 15% stay.
**Label noise:** 7% of true fraud is never reported; 0.3% of legitimate tx is mis-reported.
**Known limits:** behaviour parameters are assumptions, not upay statistics; hour-of-day is shared by fraud and legit; no seasonality or campaigns. Replace with controlled upay data in the validation stage.
