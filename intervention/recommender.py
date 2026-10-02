from .policies import policy
def recommend(balance, tainted_amount, cashout_probability, evidence):
    ratio=tainted_amount/max(balance,1); return {"amount":tainted_amount,"scope":policy("wallet",ratio,cashout_probability)["scope"],"rationale":"; ".join(evidence),"confidence":round(.55+.35*cashout_probability,2),"collateral_estimate":max(0,balance-tainted_amount),"requires_human_approval":True,"trace_id":"intelligence-demo-001"}
