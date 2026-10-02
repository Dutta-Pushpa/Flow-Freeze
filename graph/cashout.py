def find_cashout_points(edges): return [e for e in edges if e.get("is_cashout") or e.get("channel")=="agent"]
