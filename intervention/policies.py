def policy(scope, taint_ratio, cashout_probability):
    if cashout_probability>.75 and taint_ratio<.85: return {"scope":"wallet-level partial hold","requires_human_approval":True}
    if cashout_probability>.75: return {"scope":"wallet-level hold","requires_human_approval":True}
    return {"scope":"monitor and request context","requires_human_approval":True}
