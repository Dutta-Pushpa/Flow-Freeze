from ml.fraud_model import FraudModel
def test_fraud_model_fallback_score():
    assert FraudModel().predict_proba([[1,1,1,1,1,1]])[0][1] > .5
