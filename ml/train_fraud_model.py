"""Train both supervised models from labeled scenario data and persist artifacts."""
from pathlib import Path
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, accuracy_score
from ml.features import build_features, FEATURE_COLUMNS
from ml.fraud_model import FraudModel
from ml.next_move_model import NextMoveModel
DATA=Path("data/processed/generated_transactions_features.csv"); MODELS=Path("models"); EVAL=Path("data/processed/evaluation.json")

def metric_dict(y_true,y_pred,proba=None):
    tn,fp,fn,tp=confusion_matrix(y_true,y_pred,labels=[0,1]).ravel(); precision=tp/max(tp+fp,1); recall=tp/max(tp+fn,1); f1=2*precision*recall/max(precision+recall,1e-9); out={"precision":round(float(precision),6),"recall":round(float(recall),6),"f1":round(float(f1),6),"false_positives":int(fp),"false_negatives":int(fn),"support":int(len(y_true))}
    if proba is not None and len(set(y_true))==2: out["roc_auc"]=round(float(roc_auc_score(y_true,proba)),6)
    return out

def train_and_evaluate():
    if not DATA.exists(): raise FileNotFoundError(f"{DATA} missing; run python -m data_generator.generate_transactions")
    df=pd.read_csv(DATA); required={"is_fraud","next_action"}-set(df.columns)
    if required: raise ValueError(f"labeled dataset missing columns: {sorted(required)}")
    X=build_features(df); y=df.is_fraud.astype(int); actions=df.next_action.astype(str)
    train_idx,test_idx=train_test_split(range(len(df)),test_size=.25,random_state=42,stratify=y)
    X_train,X_test=X.iloc[train_idx],X.iloc[test_idx]; y_train,y_test=y.iloc[train_idx],y.iloc[test_idx]; a_train,a_test=actions.iloc[train_idx],actions.iloc[test_idx]
    fraud=FraudModel().fit(X_train,y_train); next_move=NextMoveModel().fit(X_train,a_train)
    MODELS.mkdir(exist_ok=True); fraud.save(MODELS/"fraud_model.joblib"); next_move.save(MODELS/"next_move_model.joblib")
    pred=fraud.predict(X_test); proba=fraud.predict_proba(X_test)[:,1]
    slices={}
    for name,mask in [("new_accounts",df.account_age_days.iloc[test_idx]<90),("old_accounts",df.account_age_days.iloc[test_idx]>=90),("app",df.channel.iloc[test_idx].eq("app")),("ussd",df.channel.iloc[test_idx].eq("ussd")),("agent",df.channel.iloc[test_idx].eq("agent")),("merchant",df.merchant_flag.iloc[test_idx].eq(1)),("personal",df.merchant_flag.iloc[test_idx].eq(0))]:
        positions=[i for i,m in enumerate(mask.tolist()) if m]
        slices[name]=metric_dict(y_test.iloc[positions],pred[positions],proba[positions]) if positions else {"support":0}
    next_pred=next_move.model.predict(X_test); evaluation={"experiment":{"dataset":str(DATA),"model_artifacts":[str(MODELS/"fraud_model.joblib"),str(MODELS/"next_move_model.joblib")],"seed":42,"train_rows":len(train_idx),"test_rows":len(test_idx),"feature_columns":FEATURE_COLUMNS,"scenario_count":df.scenario.nunique(),"scenarios":sorted(df.scenario.unique().tolist())},"fraud":{"model":"RandomForestClassifier","test":metric_dict(y_test,pred,proba)},"next_move":{"model":"RandomForestClassifier","accuracy":round(float(accuracy_score(a_test,next_pred)),6),"classes":sorted(actions.unique().tolist())},"slices":slices}
    EVAL.write_text(json.dumps(evaluation,indent=2)); return evaluation

if __name__=="__main__": print(json.dumps(train_and_evaluate(),indent=2))
