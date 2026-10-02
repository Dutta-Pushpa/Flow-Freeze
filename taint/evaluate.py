def compare_methods(balance, reported_amount): return {"proportional":proportional(balance,reported_amount),"whole_balance":{"tainted_amount":balance,"ratio":1.0}}
def proportional(balance, amount): return {"tainted_amount":min(balance,amount),"ratio":min(1,amount/max(balance,1))}
