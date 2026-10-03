"""Graph analytics for mule / layering discovery (pure Python, no heavy dependency)."""
from collections import defaultdict

def wallet_graph_features(edges):
    out_n, in_n, vol_in, vol_out = defaultdict(set), defaultdict(set), defaultdict(float), defaultdict(float)
    for e in edges:
        s, r, a = e["sender_wallet"], e["receiver_wallet"], float(e.get("amount", e.get("amount_bdt", 0)))
        out_n[s].add(r); in_n[r].add(s); vol_out[s] += a; vol_in[r] += a
    return {w: {"fan_in": len(in_n[w]), "fan_out": len(out_n[w]), "pass_through_ratio": round(min(vol_in[w], vol_out[w]) / max(vol_in[w], vol_out[w], 1), 3)}
            for w in set(out_n) | set(in_n)}

def find_cycles(edges, min_size=3):
    """Strongly connected components (Tarjan, iterative): circular flows are a classic layering signature."""
    adj = defaultdict(list)
    for e in edges: adj[e["sender_wallet"]].append(e["receiver_wallet"])
    nodes = set(adj) | {v for vs in adj.values() for v in vs}; idx, low, on, st, res, n = {}, {}, set(), [], [], [0]
    for root in nodes:
        if root in idx: continue
        work = [(root, iter(adj[root]))]; idx[root] = low[root] = n[0]; n[0] += 1; st.append(root); on.add(root)
        while work:
            v, it = work[-1]
            for w in it:
                if w not in idx: idx[w] = low[w] = n[0]; n[0] += 1; st.append(w); on.add(w); work.append((w, iter(adj[w]))); break
                if w in on: low[v] = min(low[v], idx[w])
            else:
                work.pop()
                if work: low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == idx[v]:
                    comp = []
                    while True:
                        w = st.pop(); on.discard(w); comp.append(w)
                        if w == v: break
                    if len(comp) >= min_size: res.append(sorted(comp))
    return res

def suspicious_hubs(edges, fan_threshold=8, pass_through=0.7):
    f = wallet_graph_features(edges)
    return sorted([{"wallet": w, **v} for w, v in f.items() if (v["fan_in"] >= fan_threshold or v["fan_out"] >= fan_threshold) and v["pass_through_ratio"] >= pass_through], key=lambda x: -x["pass_through_ratio"])
