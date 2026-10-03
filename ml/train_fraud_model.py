"""Train + evaluate: TIME-BASED split (train 60% / validation 20% / test 20%), baselines, calibration, fairness slices, impact."""
from pathlib import Path
import json
import numpy as np, pandas as pd
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix, f1_score, log_loss, roc_auc_score, roc_curve)
from data_generator.config import TARGET_FPR, ANALYST_DELAY_MIN
from ml.anomaly import AnomalyModel
from ml.baselines import fit_logistic, rule_flags
from ml.features import FEATURE_COLUMNS, build_features
from ml.fraud_model import FraudModel
from ml.next_move_model import NextMoveModel
from intervention.impact import compute_impact
DATA = Path("data/processed/generated_transactions_features.csv"); EPISODES = Path("data/processed/episodes.csv"); WALLETS = Path("data/synthetic/wallets.csv")
MODELS = Path("models"); EVAL = Path("data/processed/evaluation.json"); IMPACT = Path("data/processed/impact.json")

def pick_threshold(y, p, target_fpr=TARGET_FPR):
    fpr, _, thr = roc_curve(y, p); ok = np.where(fpr <= target_fpr)[0]; return float(thr[ok[-1]]) if len(ok) else 1.0

def recall_at_fpr(y, p, target):
    fpr, tpr, _ = roc_curve(y, p); return float(tpr[np.searchsorted(fpr, target, side="right") - 1])

def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1); idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1); e = 0.0
    for b in range(bins):
        m = idx == b
        if m.any(): e += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(e)

def cls_metrics(y, flag):
    y = np.asarray(y); flag = np.asarray(flag).astype(int); tn, fp, fn, tp = confusion_matrix(y, flag, labels=[0, 1]).ravel()
    pr = tp / max(tp + fp, 1); rc = tp / max(tp + fn, 1)
    return {"precision": round(float(pr), 4), "recall": round(float(rc), 4), "f1": round(float(2 * pr * rc / max(pr + rc, 1e-9)), 4), "false_positives": int(fp), "false_negatives": int(fn),
            "support": int(len(y)), "positives": int(y.sum()), "fpr": round(float(fp / max(fp + tn, 1)), 4)}

def score_metrics(y, p, thr, flag=None):
    flag = (p >= thr) if flag is None else flag
    return {**cls_metrics(y, flag), "roc_auc": round(float(roc_auc_score(y, p)), 4), "pr_auc": round(float(average_precision_score(y, p)), 4),
            "recall_at_1pct_fpr": round(recall_at_fpr(y, p, .01), 4), "recall_at_2pct_fpr": round(recall_at_fpr(y, p, .02), 4), "threshold": round(float(thr), 6)}

def slice_report(df, y, flag, masks):
    out = {}
    for name, m in masks.items():
        m = np.asarray(m)
        if m.sum() == 0: out[name] = {"support": 0}; continue
        r = cls_metrics(y[m], flag[m]); neg = int((y[m] == 0).sum()); r["negatives"] = neg
        if r["positives"] == 0: r.update({"precision": None, "recall": None, "f1": None})
        out[name] = r
    return out

def train_and_evaluate():
    if not DATA.exists(): raise FileNotFoundError(f"{DATA} missing; run python -m data_generator.generate_transactions")
    df = pd.read_csv(DATA).sort_values("ts_min").reset_index(drop=True); n = len(df); a, b = int(n * .6), int(n * .8)
    X = build_features(df); y = df.is_fraud.astype(int).to_numpy()
    tr, va, te = slice(0, a), slice(a, b), slice(b, n)
    fraud = FraudModel().fit(X.iloc[tr], pd.Series(y[tr], index=X.index[tr])); p_va = fraud.predict_proba(X.iloc[va])[:, 1]; p_te = fraud.predict_proba(X.iloc[te])[:, 1]
    amt = np.expm1(X["amount_log"].to_numpy())          # alert rule = expected loss: P(fraud) x amount >= tau (business rule, tau tuned on validation)
    thr = pick_threshold(y[va], p_va * amt[va]); fraud.threshold = thr
    lr = fit_logistic(X.iloc[tr], y[tr]); l_va, l_te = lr.predict_proba(X.iloc[va])[:, 1], lr.predict_proba(X.iloc[te])[:, 1]; lthr = pick_threshold(y[va], l_va * amt[va])
    anom = AnomalyModel().fit(X.iloc[tr][y[tr] == 0]); a_va, a_te = anom.percentile(X.iloc[va]), anom.percentile(X.iloc[te]); athr = pick_threshold(y[va], a_va)
    rules_te = rule_flags(X.iloc[te]).to_numpy()
    # ---- next-move model (transfers only: where does the money go AFTER it lands?) ----
    tmask = (df.cashout_flag == 0).to_numpy(); idx = np.arange(n); ntr, nva, nte = idx[tr][tmask[tr]], idx[va][tmask[va]], idx[te][tmask[te]]
    nm = NextMoveModel().fit(X.iloc[ntr], df.next_action.iloc[ntr]); pn = nm.predict_proba(X.iloc[nte]); cls = list(nm.model.classes_); yn = df.next_action.iloc[nte].to_numpy()
    pred_n = np.array(cls)[pn.argmax(1)]; maj = df.next_action.iloc[ntr].mode()[0]; prior = df.next_action.iloc[ntr].value_counts(normalize=True).reindex(cls).to_numpy()
    ci = cls.index("cashout"); yc = (yn == "cashout").astype(int)
    th_table = {str(t): {"precision": round(float(((pn[:, ci] >= t) & (yc == 1)).sum() / max((pn[:, ci] >= t).sum(), 1)), 3), "recall": round(float(((pn[:, ci] >= t) & (yc == 1)).sum() / max(yc.sum(), 1)), 3), "flagged": int((pn[:, ci] >= t).sum())} for t in (.3, .5, .7)}
    nextm = {"model": "HistGradientBoosting + sigmoid calibration", "accuracy": round(float((pred_n == yn).mean()), 4), "macro_f1": round(float(f1_score(yn, pred_n, average="macro")), 4),
             "majority_class_baseline_accuracy": round(float((yn == maj).mean()), 4), "log_loss": round(float(log_loss(yn, pn, labels=cls)), 4),
             "prior_baseline_log_loss": round(float(log_loss(yn, np.tile(prior, (len(yn), 1)), labels=cls)), 4), "cashout_pr_auc": round(float(average_precision_score(yc, pn[:, ci])), 4),
             "cashout_roc_auc": round(float(roc_auc_score(yc, pn[:, ci])), 4), "cashout_prevalence": round(float(yc.mean()), 4), "cashout_threshold_table": th_table, "classes": cls, "test_rows": int(len(nte))}
    # ---- fairness / error slices on the test window (operating threshold from validation) ----
    d = df.iloc[te].reset_index(drop=True); yt = y[te]; flag = (p_te * amt[te]) >= thr; neg_legit = d.true_fraud.to_numpy() == 0
    masks = {"new_accounts_<90d": d.account_age_days < 90, "old_accounts_>=90d": d.account_age_days >= 90, "channel_app": d.channel == "app", "channel_ussd": d.channel == "ussd", "channel_agent": d.channel == "agent",
             "to_merchant": d.merchant_flag == 1, "to_non_merchant": d.merchant_flag == 0, "legit_look_alike(unusual)": (d.legit_profile == "unusual"), "legit_merchant_traffic": (d.legit_profile == "merchant"), "legit_normal": (d.legit_profile == "normal")}
    slices = slice_report(d, yt, flag, {k: v.to_numpy() for k, v in masks.items()})
    grp = [slices[k]["fpr"] for k in ("channel_app", "channel_ussd", "channel_agent", "new_accounts_<90d", "old_accounts_>=90d") if slices.get(k, {}).get("negatives", 0) >= 50]
    ratio = round(max(grp) / max(min(grp), 1e-4), 2) if grp else None
    fairness = {"max_fpr_ratio_across_groups": ratio, "flag": "REVIEW: false-positive rate differs >2x between groups" if ratio and ratio > 2 else "ok",
                "most_harmed_legit_group": max((k for k in ("legit_look_alike(unusual)", "legit_merchant_traffic", "legit_normal") if slices[k].get("negatives", 0)), key=lambda k: slices[k]["fpr"]), "note": "FPR = share of legitimate transactions that would be alerted."}
    fm = {**score_metrics(yt, p_te, thr, flag), "alert_rule": "P(fraud) x amount_bdt >= threshold (expected-loss rule)"}
    evaluation = {"experiment": {"dataset": str(DATA), "model_artifacts": [str(MODELS / "fraud_model.joblib"), str(MODELS / "next_move_model.joblib"), str(MODELS / "anomaly_model.joblib")], "seed": 42,
                  "split": "time-based: train first 60% / validation next 20% / test last 20%", "train_rows": a, "val_rows": b - a, "test_rows": n - b, "fraud_rate_train": round(float(y[tr].mean()), 4), "fraud_rate_test": round(float(yt.mean()), 4),
                  "label_noise": "7% of true fraud unlabeled, 0.3% of legit mislabeled", "operating_point": f"expected-loss threshold chosen on validation for <= {TARGET_FPR:.0%} false-positive rate", "feature_columns": FEATURE_COLUMNS,
                  "scenario_count": int(df.scenario.nunique()), "scenarios": sorted(df.scenario.unique().tolist())},
                  "fraud": {"model": "HistGradientBoosting + isotonic calibration", "test": {**fm, "brier": round(float(brier_score_loss(yt, p_te)), 4), "ece": round(ece(yt, p_te), 4), "chance_pr_auc": round(float(yt.mean()), 4)},
                  "baselines": {"fixed_rules": {**cls_metrics(yt, rules_te), "note": "binary rule alerts"}, "logistic_regression": score_metrics(yt, l_te, lthr, (l_te * amt[te]) >= lthr), "isolation_forest_unsupervised": score_metrics(yt, a_te, athr)}},
                  "next_move": nextm, "slices": slices, "fairness": fairness}
    MODELS.mkdir(exist_ok=True); fraud.save(MODELS / "fraud_model.joblib"); nm.save(MODELS / "next_move_model.joblib"); anom.save(MODELS / "anomaly_model.joblib")
    EVAL.write_text(json.dumps(evaluation, indent=2))
    eps = pd.read_csv(EPISODES); wallets = pd.read_csv(WALLETS)
    impact = compute_impact(d, eps, wallets, pd.Series(flag), pd.Series(rules_te.astype(bool)), ANALYST_DELAY_MIN)
    best = impact["strategies"]["FlowFreeze + proportional hold"]; days = round((d.ts_min.max() - d.ts_min.min()) / 1440, 1)
    impact["overview"] = {"activeIncidents": best["episodes_caught"], "suspiciousFlows": best["alerts"], "valueAtRisk": best["value_at_risk_bdt"], "valuePreserved": best["preserved_bdt"], "preservedChange": impact["preserved_change_vs_rules_pct"],
                          "falseAlerts": best["false_alerts"], "episodes": best["episodes"], "windowLabel": f"{days}-day simulated test window", "basis": "computed by intervention/impact.py on held-out synthetic data"}
    IMPACT.write_text(json.dumps(impact, indent=2)); return evaluation

if __name__ == "__main__": print(json.dumps(train_and_evaluate(), indent=2)[:6000])
