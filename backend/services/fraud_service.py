from ml.explain import explain_prediction
def score_incident(amount: float, balance: float, cashout_probability: float = .81):
    ratio=amount/max(balance,1); score=min(.99,.45+.35*cashout_probability+.2*min(1,ratio))
    factors={"cashout_probability":round(cashout_probability,3),"taint_ratio":round(ratio,3),"rapid_forwarding":.92}
    return {"risk_score":round(score,4),"class":"suspicious" if score>=.75 else "review", "explanation":explain_prediction(score,factors)}
