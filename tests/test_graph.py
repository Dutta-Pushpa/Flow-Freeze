from graph.tracer import trace_flow
def test_graph_traces_downstream():
    edges=[{"sender_wallet":"A","receiver_wallet":"B","amount":10},{"sender_wallet":"B","receiver_wallet":"C","amount":8}]
    assert len(trace_flow(edges,"A")) == 2
