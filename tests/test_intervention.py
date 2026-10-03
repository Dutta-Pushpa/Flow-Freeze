from intervention.recommender import recommend
from intervention.impact import compute_impact
def test_recommendation_requires_human_and_unique_trace():
    a = recommend(22000, 15000, .81, ["x"], fraud_probability=.7, alert=True); b = recommend(22000, 15000, .81, ["x"])
    assert a["requires_human_approval"] and a["collateral_estimate"] == 7000 and a["trace_id"] != b["trace_id"] and a["hold_max_hours"] > 0 and a["confidence"] == .7
def test_low_cashout_probability_only_monitors():
    assert recommend(22000, 15000, .1, ["x"])["scope"] == "monitor and request context"
def test_impact_file_is_computed():
    import json, pathlib
    i = json.loads(pathlib.Path("data/processed/impact.json").read_text()); s = i["strategies"]
    assert s["FlowFreeze + proportional hold"]["legit_value_held_bdt"] < s["FlowFreeze + whole-wallet hold"]["legit_value_held_bdt"]
