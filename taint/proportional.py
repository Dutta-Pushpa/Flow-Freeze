"""Multi-hop proportional ('haircut') taint tracing."""
from collections import defaultdict

def proportional_taint(balance, reported_amount, linked_amount=None):
    """Single-wallet estimate: the reported value is tainted, the rest of the balance is not."""
    linked = reported_amount if linked_amount is None else linked_amount
    return {"tainted_amount": min(balance, linked), "ratio": round(min(1, linked / max(balance, 1)), 4), "method": "proportional"}

def propagate_taint(edges, seeds, opening_balances=None, method="proportional"):
    """Replay time-ordered edges {sender_wallet, receiver_wallet, amount, [minutes]} and track tainted value per wallet.
    seeds: {wallet: tainted_amount_it_holds_at_start}. Methods:
      proportional : every outgoing payment carries the sender's current taint ratio (haircut)
      whole_balance: any outgoing payment from a tainted wallet is fully tainted (poison)
      fifo         : oldest money leaves first (tainted money leaves first if it arrived first)
    Returns per-wallet balance/tainted and the tainted value that reached each terminal wallet (e.g. CASH)."""
    bal = defaultdict(float, opening_balances or {}); tnt = defaultdict(float)
    lots = defaultdict(list)
    for w, t in seeds.items():
        bal[w] = max(bal[w], t); tnt[w] = t
        if bal[w] - t > 0: lots[w].append([bal[w] - t, False])
        lots[w].append([t, True])
    for w, b in (opening_balances or {}).items():
        if w not in seeds and b > 0: lots[w].append([b, False])
    moved = []
    for e in sorted(edges, key=lambda e: e.get("minutes", 0)):
        s, r, a = e["sender_wallet"], e["receiver_wallet"], float(e["amount"])
        a = min(a, bal[s]) if bal[s] > 0 else a
        if method == "proportional": mv = a * (tnt[s] / bal[s]) if bal[s] > 0 else 0.0
        elif method == "whole_balance": mv = a if tnt[s] > 0 else 0.0
        elif method == "fifo":
            need, mv, q = a, 0.0, lots[s]
            while need > 1e-9 and q:
                take = min(q[0][0], need); mv += take if q[0][1] else 0; q[0][0] -= take; need -= take
                if q[0][0] <= 1e-9: q.pop(0)
        else: raise ValueError("unknown taint method")
        mv = min(mv, tnt[s], a)
        bal[s] -= a; tnt[s] -= mv; bal[r] += a; tnt[r] += mv
        if method == "fifo": lots[r].append([a - mv, False]) if a - mv > 0 else None; lots[r].append([mv, True]) if mv > 0 else None
        moved.append({"from": s, "to": r, "amount": a, "tainted": round(mv, 2)})
    return {"method": method, "wallets": {w: {"balance": round(bal[w], 2), "tainted": round(tnt[w], 2)} for w in set(bal) | set(tnt)}, "flows": moved}
