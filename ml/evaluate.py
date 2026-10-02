import pandas as pd
from sklearn.metrics import precision_score,recall_score,f1_score
def evaluate(y_true,y_pred): return {"precision":float(precision_score(y_true,y_pred,zero_division=0)),"recall":float(recall_score(y_true,y_pred,zero_division=0)),"f1":float(f1_score(y_true,y_pred,zero_division=0))}
def compare(baseline,flowfreeze): return pd.DataFrame([{"model":"baseline",**baseline},{"model":"flowfreeze",**flowfreeze}])
