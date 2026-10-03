from ml.training import predict_fraud

def score_transaction(transaction: dict):
    prediction=predict_fraud(transaction); probability=prediction["fraud_probability"]
    return {**prediction,"class":"alert" if prediction["alert"] else "low_risk"}

def score_incident(amount: float, balance: float, features=None):
    transaction={"amount_bdt":amount,**(features or {})}
    result=score_transaction(transaction); result["taint_ratio"]=round(amount/max(balance,1),4); return result
