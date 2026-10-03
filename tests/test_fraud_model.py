import json, pathlib, numpy as np, pandas as pd, pytest

def test_untrained_model_refuses_inference():
    from ml.fraud_model import FraudModel
    with pytest.raises(RuntimeError): FraudModel().predict_proba(pd.DataFrame([[1] * 15]))

def test_metrics_are_realistic_and_beat_baselines():
    e = json.loads(pathlib.Path("data/processed/evaluation.json").read_text()); t = e["fraud"]["test"]; b = e["fraud"]["baselines"]
    assert t["roc_auc"] < 0.995 and t["pr_auc"] < 0.995                    # not circular / not perfect
    assert t["pr_auc"] > b["logistic_regression"]["pr_auc"]                # beats a simple linear model
    assert t["recall"] > b["fixed_rules"]["recall"]                         # beats fixed rules
    assert t["ece"] < 0.05                                                  # calibrated
    assert "time-based" in e["experiment"]["split"]

def test_persisted_model_scores_behavioral_contrast():
    from ml.training import predict_fraud
    normal = {"amount": 800, "sender_velocity": 1, "receiver_velocity": 1, "new_relationship": 0, "rapid_forwarding": 0, "hour": 14, "account_age_days": 600, "receiver_age_days": 900, "merchant_flag": 1}
    bad = {"amount": 15000, "sender_velocity": 6, "receiver_velocity": 4, "new_relationship": 1, "rapid_forwarding": 1, "amount_vs_sender_avg": 5.7, "hour": 2, "account_age_days": 19, "receiver_age_days": 25}
    a, b = predict_fraud(normal), predict_fraud(bad)
    assert 0 <= a["fraud_probability"] < b["fraud_probability"] <= 1 and b["alert"] and not a["alert"] and a["trace_id"] != b["trace_id"]

def test_shapley_is_additive():
    from ml.explain import shapley
    f = lambda A: 1 / (1 + np.exp(-(A @ np.array([1.0, -2.0, .5]) )))
    x, b = np.array([1., 1., 2.]), np.zeros(3); phi, v, v0 = shapley(f, x, b)
    assert abs(phi.sum() - (v - v0)) < 1e-9

def test_explanation_matches_model_output():
    from ml.training import explain_fraud, predict_fraud
    x = {"amount": 15000, "new_relationship": 1, "rapid_forwarding": 1, "account_age_days": 19, "receiver_age_days": 25, "sender_velocity": 6}
    ex = explain_fraud(x, top=15); assert abs(ex["fraud_probability"] - predict_fraud(x)["fraud_probability"]) < 1e-3
    assert abs(sum(f["contribution"] for f in ex["factors"]) - (ex["fraud_probability"] - ex["baseline_probability"])) < 0.02

def test_next_move_probabilities_sum_to_one():
    from ml.training import predict_next_move
    m = predict_next_move({"amount": 9000, "new_relationship": 1}); assert abs(m["forward"] + m["cashout"] + m["other"] - 1) < 0.01
