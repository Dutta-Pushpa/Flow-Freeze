def proportional_taint(balance, reported_amount, linked_amount=None):
    linked=reported_amount if linked_amount is None else linked_amount; return {"tainted_amount":min(balance,linked),"ratio":round(min(1,linked/max(balance,1)),4),"method":"proportional"}
