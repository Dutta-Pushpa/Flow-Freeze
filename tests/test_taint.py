import pytest
from taint.proportional import propagate_taint, proportional_taint
EDGES = [{"sender_wallet": "W1", "receiver_wallet": "W4", "amount": 15000, "minutes": 1}, {"sender_wallet": "W4", "receiver_wallet": "W2", "amount": 7000, "minutes": 3},
         {"sender_wallet": "W4", "receiver_wallet": "AG", "amount": 8000, "minutes": 4}, {"sender_wallet": "AG", "receiver_wallet": "CASH", "amount": 8000, "minutes": 5}]

@pytest.mark.parametrize("method", ["proportional", "fifo", "whole_balance"])
def test_taint_is_conserved(method):
    r = propagate_taint(EDGES, {"W1": 15000}, {"W4": 7000, "AG": 41000}, method)
    assert abs(sum(w["tainted"] for w in r["wallets"].values()) - 15000) < 1

def test_proportional_leaves_less_collateral_than_whole_balance():
    p = propagate_taint(EDGES, {"W1": 15000}, {"W4": 7000, "AG": 41000}, "proportional")["wallets"]
    w = propagate_taint(EDGES, {"W1": 15000}, {"W4": 7000, "AG": 41000}, "whole_balance")["wallets"]
    assert p["CASH"]["tainted"] < w["CASH"]["tainted"]

def test_single_wallet_estimate():
    r = proportional_taint(22000, 15000); assert r["tainted_amount"] == 15000 and r["ratio"] < 1
