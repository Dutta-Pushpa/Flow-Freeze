from taint.proportional import proportional_taint
def test_proportional_taint_preserves_collateral():
    result=proportional_taint(22000,15000)
    assert result["tainted_amount"] == 15000 and result["ratio"] < 1
