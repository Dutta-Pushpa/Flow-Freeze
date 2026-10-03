# FlowFreeze reference architecture

```text
Synthetic/Public Data → Feature & Context Layer → ML/AI Engine → Explanation / Recommendation → User or Operator Action → Measurable Outcome → Feedback Loop
```

## Separation of responsibilities

`data_generator/` owns reproducible synthetic MFS transactions and scenarios. `ml/features.py` prepares features. `ml/fraud_model.py` and `ml/next_move_model.py` perform inference. `intervention/policies.py` and `intervention/recommender.py` keep business rules and proportional action scope outside model or LLM text. `backend/services/explanation_service.py` retrieves evidence and can optionally call a server-side OpenAI-compatible LLM for summarization, but cannot alter risk score, amount, scope, or approval requirement.

The Node.js API remains the analyst-facing BFF. The FastAPI service in `backend/main.py` is the model API that can be deployed separately. PostgreSQL is the durable target for transactions, features, predictions, decisions, and feedback. Managed MySQL remains supported for the current Webdev prototype audit tables.

## Stack

Python, Pandas, scikit-learn (gradient boosting + calibration, Isolation Forest), exact Shapley attribution, TF-IDF evidence retrieval, FastAPI with enforced bearer-token RBAC, Node.js/Express BFF, React console. Persistence: the Node BFF uses the managed MySQL audit adapter for the demo; the FastAPI service writes a hash-chained JSONL audit log. A production deployment would move both to PostgreSQL (see docs/api.md). No XGBoost/LightGBM/PyTorch is used.
