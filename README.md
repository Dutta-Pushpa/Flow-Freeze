# FlowFreeze

FlowFreeze is a synthetic-data risk-operations console for a Bangladesh-style MFS. It helps analysts trace suspicious digital-money movement, estimate potentially tainted value, predict likely next movement or cash-out, and review a proportionate intervention recommendation before recording an accountable decision.

> **Safety boundary:** this is decision support. It does not autonomously confiscate, reverse, refund, or legally freeze customer money. Recommendations require authorized human approval, and the included data is synthetic.

## Reference architecture

```text
INPUT → INTELLIGENCE → ACTION

Synthetic/Public Data
→ Feature & Context Layer
→ ML/AI Engine
→ Explanation / Recommendation
→ User or Operator Action
→ Measurable Outcome
→ Feedback Loop
```

Data preparation is separated from inference. Business policies are separate from model scores. Model outputs carry structured factors, confidence, collateral estimate, evidence, and a trace ID. Optional GenAI/RAG is server-side and grounded in retrieved evidence; it cannot change risk score, action amount, scope, or approval requirements.

## Stack

| Layer | Implementation |
|---|---|
| Data | Python, Pandas, deterministic synthetic MFS transactions/scenarios |
| ML | scikit-learn classifier, XGBoost/LightGBM dependency surface, PyTorch-ready extension point |
| GenAI | Optional OpenAI-compatible LLM with evidence retrieval and guardrails |
| API | FastAPI model service plus Node.js/Express analyst-facing BFF |
| Storage | PostgreSQL-ready SQLAlchemy/psycopg configuration; Webdev-managed MySQL audit adapter |
| Frontend | React/Vite analyst console with AI/ML observability page |
| Monitoring | `/health`, model pipeline metadata, API audit trail, decision feedback endpoint |

## Run the app

```bash
npm install
npm run build
npm start
```

Open `http://localhost:3000`. The Webdev Preview uses the same port and serves the React analyst console.

## Run the intelligence service

```bash
python3 -m pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The FastAPI service exposes `/health`, `/api/v1/incidents/score`, `/api/v1/transactions/validate`, `/api/v1/graph/trace`, `/api/v1/predictions/next-move`, `/api/v1/interventions/recommend`, and `/api/v1/feedback`. Set `PYTHON_API_URL=http://127.0.0.1:8000` for the Node BFF to proxy model requests. `docker compose up` provides PostgreSQL and the intelligence container.

## AI/ML integration

The `/intelligence` page displays the full pipeline, model stack, GenAI/RAG boundary, and a live reference inference. The Node routes `/api/intelligence/health` and `/api/intelligence/recommend` call the FastAPI service when available and return an explicit 503 when trained intelligence is unavailable; no fake prediction is returned. The Python recommendation combines structured risk, proportional taint, next-move likelihood, and business policy before producing a human-gated action.

Set `FLOWFREEZE_ENABLE_LLM=true` and provide server-side `OPENAI_API_KEY`/`OPENAI_API_BASE` only when optional LLM summarization is desired. The LLM layer is never the sole decision-maker.

## Requested structure

The repository includes the requested `data_generator/`, `notebooks/`, `ml/`, `backend/`, `tests/`, `graph/`, `taint/`, `intervention/`, `docs/`, `data/`, and `demo/` folders, including the exact Python file names for data generation, feature preparation, fraud/next-move models, graph tracing, taint methods, interventions, FastAPI routes/services, and tests.

## Validation

```bash
npm run check
python3 -m compileall -q data_generator ml graph taint intervention backend
python3 -m pytest -q tests
```

Current validation covers six Python tests plus the JavaScript production build. The live smoke path verifies the FastAPI health and grounded recommendation endpoints and the Node proxy.

## Demo story

Start on Overview, open `INC-2407`, inspect `Victim → W1 → W4 → Agent 7 → Cash-out`, review Wallet W4, and open the recommendation. The recommended ৳15,000 partial hold follows the proportional taint estimate while leaving an estimated ৳7,000 of legitimate value outside the action. Use What-if simulator, then visit AI / ML observability to run the same scenario through the API and inspect the retrieved evidence and trace ID. Record a decision and review the Audit page.

## Persisted ML pipeline

The AI/ML path is artifact-backed rather than a deterministic demo constant:

```bash
python -m data_generator.generate_transactions
python -m ml.train_fraud_model
```

This creates labeled behavioral scenarios, engineers transaction features, trains separate fraud and next-action `RandomForestClassifier` models, saves `models/fraud_model.joblib` and `models/next_move_model.joblib`, and writes held-out metrics to `data/processed/evaluation.json`. The API loads those artifacts and rejects inference when they are missing. The Node BFF accepts transaction-specific behavioral features through `/api/fraud-score` and `/api/predictions/:walletId`; it does not return a fake probability fallback.
