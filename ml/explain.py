"""Traceable explanations: structured factors first, optional LLM second."""
def explain_prediction(score, factors): return {"score":round(float(score),4),"factors":[{"name":k,"contribution":v} for k,v in factors.items()],"method":"structured_feature_attribution","free_form_llm_used":False}
