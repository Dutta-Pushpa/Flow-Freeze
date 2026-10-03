from graph.tracer import trace_flow
from graph.features import find_cycles, suspicious_hubs
def test_graph_traces_downstream():
    assert len(trace_flow([{"sender_wallet": "A", "receiver_wallet": "B", "amount": 10}, {"sender_wallet": "B", "receiver_wallet": "C", "amount": 8}], "A")) == 2
def test_cycle_and_hub_detection():
    e = [{"sender_wallet": a, "receiver_wallet": b, "amount": 100} for a, b in [("A", "B"), ("B", "C"), ("C", "A")]]
    assert find_cycles(e) == [["A", "B", "C"]]
    hub = [{"sender_wallet": f"S{i}", "receiver_wallet": "H", "amount": 100} for i in range(9)] + [{"sender_wallet": "H", "receiver_wallet": "X", "amount": 800}]
    assert suspicious_hubs(hub)[0]["wallet"] == "H"
