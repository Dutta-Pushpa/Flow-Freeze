from taint.proportional import propagate_taint
def whole_balance_taint(balance, reported_amount): return {"tainted_amount": balance, "ratio": 1.0, "method": "whole_balance"}
def whole_balance_trace(edges, seeds, opening_balances=None): return propagate_taint(edges, seeds, opening_balances, "whole_balance")
