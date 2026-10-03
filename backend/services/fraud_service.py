from ml.training import predict_fraud
from ml.explain import explain_prediction

def score_incident(amount: float, balance: float, cashout_probability=None, features=None):
    import math
    payload={"amount":amount,"amount_log":math.log1p(max(amount,1)),"sender_velocity":5,"receiver_velocity":4,"hop_count":2,"cashout_flag":int(bool(cashout_probability and cashout_probability>.5)),"new_relationship":1,"account_age_days":19,"channel":"app","merchant_flag":0,**(features or {})}
    prediction=predict_fraud(payload); score=prediction["risk_score"]
    factors={"model_probability":score,"taint_ratio":round(amount/max(balance,1),3),"model":prediction["model"]}
    return {"risk_score":score,"prediction":prediction["prediction"],"class":"suspicious" if score>=.5 else "review","model":prediction["model"],"explanation":explain_prediction(score,factors),"factors":factors}
