from taint.proportional import propagate_taint

def compare_methods(edges, seeds, opening_balances, truth_wallet="CASH"):
    """Run all three taint rules on the same multi-hop flow and report who ends up holding 'tainted' value.
    Over-attribution (taint assigned to money that was legitimate) is the collateral-damage proxy."""
    out = {}
    for m in ("proportional", "fifo", "whole_balance"):
        r = propagate_taint(edges, seeds, opening_balances, m); w = r["wallets"]
        out[m] = {"tainted_at_cashout": w.get(truth_wallet, {}).get("tainted", 0), "total_tainted_in_system": round(sum(v["tainted"] for v in w.values()), 2),
                  "wallets": {k: v for k, v in w.items() if v["tainted"] > 0}}
    return out
