from graph.tracer import trace_flow
def trace_transactions(edges, source): return {"source":source,"hops":trace_flow(edges,source),"cashout_points":[e for e in edges if e.get("is_cashout") or e.get("channel")=="agent"]}
