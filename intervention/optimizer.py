def optimize(balance, tainted_amount, delay_minutes=0): return {"recommended_amount":min(balance,round(tainted_amount*(1+delay_minutes*.03))),"delay_minutes":delay_minutes}
