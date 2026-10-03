from __future__ import annotations
from collections import defaultdict

def simulate_flow(edges, source, delay_minutes, hold_ratio, initial_taint):
    """Replay graph edges in time order; delay changes which edges execute before the hold."""
    ordered = sorted(edges, key=lambda e: e.get("minutes", 0))
    replayed = [e for e in ordered if e.get("minutes", 0) <= delay_minutes]
    movement = sum(float(e.get("amount", 0)) for e in replayed if e.get("sender_wallet") == source or e.get("receiver_wallet") != "CASH")
    cashout = sum(float(e.get("amount", 0)) for e in replayed if e.get("is_cashout") or e.get("receiver_wallet") in {"CASH", "CASHOUT"})
    held = min(float(initial_taint), float(initial_taint) * float(hold_ratio) / 100)
    recoverable = max(0.0, min(float(initial_taint), held + max(0.0, float(initial_taint) - cashout)))
    return {"delay_minutes": delay_minutes, "hold_ratio": hold_ratio, "stages": {"delay": delay_minutes, "transaction_replay": len(replayed), "money_movement_bdt": round(movement, 2), "cash_out_bdt": round(cashout, 2), "recoverable_amount_bdt": round(recoverable, 2)}, "replayed_edges": replayed}
