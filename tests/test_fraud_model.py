import pytest

def test_untrained_model_refuses_inference():
    from ml.fraud_model import FraudModel
    with pytest.raises(RuntimeError): FraudModel().predict_proba([[1] * 12])

def test_persisted_model_scores_behavioral_contrast():
    from ml.training import predict_fraud
    normal={"amount":800,"sender_velocity":2,"receiver_velocity":2,"cashout_flag":0,"new_relationship":0,"rapid_forwarding":0,"amount_vs_sender_avg":1,"hour":14,"account_age_days":600,"device_changed":0,"merchant_flag":1,"channel":"app"}
    suspicious={"amount":15000,"sender_velocity":10,"receiver_velocity":8,"cashout_flag":1,"new_relationship":1,"rapid_forwarding":1,"amount_vs_sender_avg":4,"hour":2,"account_age_days":14,"device_changed":1,"merchant_flag":0,"channel":"ussd"}
    a,b=predict_fraud(normal),predict_fraud(suspicious)
    assert a["model"] == b["model"] == "RandomForestClassifier"
    assert b["fraud_probability"] > a["fraud_probability"]
