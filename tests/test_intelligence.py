def test_trained_models_return_predictions():
    from ml.training import predict_fraud, predict_next_move
    features = {"amount": 15000, "sender_velocity": 5, "receiver_velocity": 4, "hop_count": 2, "cashout_flag": 1, "new_relationship": 1, "account_age_days": 19, "channel": "app", "merchant_flag": 0}
    fraud = predict_fraud(features); move = predict_next_move(features)
    assert fraud["model"] == "HistGradientBoostingClassifier" and fraud["risk_score"] > .5
    assert abs(sum(move[key] for key in ("forward", "cashout", "other")) - 1) < .01

def test_graph_simulation_has_causal_stages():
    from graph.simulator import simulate_flow
    result = simulate_flow([{"sender_wallet":"W4","receiver_wallet":"AG","amount":8000,"minutes":2,"channel":"agent"},{"sender_wallet":"AG","receiver_wallet":"CASH","amount":8000,"minutes":3,"is_cashout":True}], "W4", 3, 68, 15000)
    assert list(result["stages"]) == ["delay", "transaction_replay", "money_movement_bdt", "cash_out_bdt", "recoverable_amount_bdt"]

def test_security_feedback_and_hash_chain(tmp_path, monkeypatch):
    from backend import security
    assert security.security_demo()["prompt_injection"]["blocked"]
    from backend.services import feedback_store
    monkeypatch.setattr(feedback_store, "PATH", tmp_path / "feedback.jsonl")
    event = feedback_store.record_feedback({"prediction":"fraud","analyst_decision":"approved","actual_outcome":"fraud"})
    assert event["correct"] is True and feedback_store.verify_audit_integrity()["ok"]
