"""Business-impact simulation on the held-out window: what would each detector + hold policy have preserved / wrongly held?"""
import numpy as np, pandas as pd
from data_generator.config import ANALYST_DELAY_MIN, HOLD_SAFETY_MARGIN, MIN_PER_ALERT

def _episode_outcome(ep, flagged, delay):
    if not flagged: return 0.0
    d1 = ep.first_move_delay_min
    return float(ep.amount_bdt) if (np.isnan(d1) or delay <= d1) else float(ep.amount_bdt) * (1 - float(ep.moved_fraction))

def evaluate_detector(test, eps, wallets, flag, delay=ANALYST_DELAY_MIN, margin=HOLD_SAFETY_MARGIN):
    flagged_ids = set(test.loc[flag.values, "transaction_id"]); bal = wallets.set_index("wallet_id").balance_bdt
    ep = eps[eps.first_fraud_tx_id.isin(set(test.transaction_id))]
    hit = ep.first_fraud_tx_id.isin(flagged_ids)
    pres = sum(_episode_outcome(r, h, delay) for r, h in zip(ep.itertuples(), hit))
    tp_collat_whole = float(ep.loc[hit, "mule_own_balance_bdt"].sum()); tp_collat_prop = float(sum(_episode_outcome(r, True, delay) * margin for r in ep[hit].itertuples()))
    fp = test[flag.values & (test.true_fraud.values == 0)]
    fp_whole = float(fp.receiver_wallet.map(bal).fillna(0).sum()); fp_prop = float(np.minimum(fp.amount_bdt * (1 + margin), fp.receiver_wallet.map(bal).fillna(0)).sum())
    risk = float(ep.amount_bdt.sum()); alerts = int(flag.sum())
    base = {"episodes": int(len(ep)), "episodes_caught": int(hit.sum()), "value_at_risk_bdt": risk, "preserved_bdt": round(pres), "preserved_pct": round(100 * pres / max(risk, 1), 1),
            "alerts": alerts, "false_alerts": int(len(fp)), "analyst_minutes": alerts * MIN_PER_ALERT}
    return {"whole_balance": {**base, "legit_value_held_bdt": round(tp_collat_whole + fp_whole)}, "proportional": {**base, "legit_value_held_bdt": round(tp_collat_prop + fp_prop)}}

def compute_impact(test, eps, wallets, ml_flag, rule_flag, delay=ANALYST_DELAY_MIN):
    res = {"assumptions": {"analyst_delay_min": delay, "hold_safety_margin": HOLD_SAFETY_MARGIN, "minutes_per_alert": MIN_PER_ALERT,
                           "note": "Simulation on synthetic data. Preserved = tainted value still in the wallet when the hold lands. Legit value held = money not tied to the fraud that a hold would freeze (TP collateral + false-alert holds, before release)."}}
    r = evaluate_detector(test, eps, wallets, rule_flag, delay); m = evaluate_detector(test, eps, wallets, ml_flag, delay)
    res["strategies"] = {"no_action": {"preserved_bdt": 0, "preserved_pct": 0.0, "legit_value_held_bdt": 0}, "rules + whole-wallet hold": r["whole_balance"],
                         "FlowFreeze + whole-wallet hold": m["whole_balance"], "FlowFreeze + proportional hold": m["proportional"]}
    base = r["whole_balance"]["preserved_bdt"]; res["preserved_change_vs_rules_pct"] = round(100 * (m["proportional"]["preserved_bdt"] - base) / max(base, 1), 1)
    res["collateral_reduction_vs_whole_wallet_pct"] = round(100 * (1 - m["proportional"]["legit_value_held_bdt"] / max(m["whole_balance"]["legit_value_held_bdt"], 1)), 1)
    res["delay_sensitivity_preserved_pct"] = {str(d): evaluate_detector(test, eps, wallets, ml_flag, d)["proportional"]["preserved_pct"] for d in (0, 2, 5, 10, 15, 30)}
    return res
