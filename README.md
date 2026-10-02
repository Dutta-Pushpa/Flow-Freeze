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

The `/intelligence` page displays the full pipeline, model stack, GenAI/RAG boundary, and a live reference inference. The Node routes `/api/intelligence/health` and `/api/intelligence/recommend` call the FastAPI service when available and return a safe deterministic fallback when it is not. The Python recommendation combines structured risk, proportional taint, next-move likelihood, and business policy before producing a human-gated action.

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

## Live demo

**Live deployment URL:** https://flowfreeze-cawtkvfs.manus.space/?utm_id=97757_v0_s00_e0_tv0

The hosted app runs on synthetic data only. Open the link and follow the [Demo story](#demo-story) above (start on Overview, open `INC-2407`). Analyst access is a prototype login at `/login`; no real credentials or customer data are used.

## Project overview

- **Problem:** When a customer reports a fraudulent or mistaken transfer in a mobile financial service (MFS), the money is often split and forwarded across several wallets within minutes and then cashed out at agents. Checking only the direct recipient misses downstream e-money, and once value becomes physical cash it is out of reach.
- **Proposed solution:** FlowFreeze traces the reported funds across wallets, estimates how much of each wallet is potentially tainted, predicts the likely next move (forward or cash-out), and recommends the mildest proportionate temporary intervention (for example a partial hold on the tainted amount). An authorized analyst approves, rejects or modifies the recommendation and records a reason.
- **Purpose:** Help an MFS provider contain suspected fraud faster while limiting harm to innocent users, with every step explainable and auditable. It is decision support only and never moves, reverses or refunds money.

## Features

- Overview dashboard with active incidents and value at risk.
- Incident list and incident detail (reported transaction, timeline, evidence).
- Transaction graph that traces `Victim → W1 → W4 → Agent 7 → Cash-out` and separates cash already out of reach from still-reachable e-money.
- Wallet intelligence page with balance, risk factors and proportional taint estimate.
- Intervention queue with a recommended partial hold, rationale, confidence and collateral estimate.
- Analyst approval workflow: approve, reject or modify, with a required reason.
- What-if simulator for response delay and hold size.
- Evaluation page comparing FlowFreeze with a direct-recipient-only baseline.
- AI / ML observability page that runs a reference inference through the API and shows retrieved evidence and a trace ID.
- Audit history of analyst actions.

**How the AI components are used**

| Component | Role |
|---|---|
| Fraud-risk classifier (`ml/fraud_model.py`) | Gradient-boosting classifier (scikit-learn) that scores suspicious transactions from features such as amount, velocity, hop count, cash-out flag and new relationship |
| Next-move model (`ml/next_move_model.py`) | Estimates forward, cash-out or other probabilities for a wallet, kept separate from business policy |
| Graph tracing (`graph/`) | Builds the wallet-to-wallet graph and follows downstream hops and cash-out points |
| Taint engine (`taint/`) | Deterministic, auditable proportional attribution, with a whole-balance alternative for comparison |
| Intervention engine (`intervention/`) | Policy layer that turns scores and taint into a human-gated recommendation under a collateral limit |
| Optional LLM | Writes a grounded explanation only; it cannot change the score, amount, scope or approval requirement |

## Technology stack details

- **Languages:** JavaScript (ES modules, Node.js 22) and Python 3.12.
- **Frontend:** React 18, Vite 6.
- **Backend:** Express 4 (Node BFF), FastAPI with Uvicorn and Pydantic (model service).
- **ML and data:** pandas, numpy, scikit-learn (`HistGradientBoostingClassifier`); xgboost, lightgbm and torch are listed in `requirements.txt` as optional extension points.
- **Storage:** MySQL via `mysql2` for the audit and decision tables; PostgreSQL via SQLAlchemy and psycopg in the Docker setup.
- **APIs and services:** optional OpenAI-compatible chat API for explanations; Docker and Docker Compose.

## Requirements

- Node.js 22 (or 20+) and npm.
- Python 3.12 and pip.
- Optional: Docker and Docker Compose, a MySQL or PostgreSQL database, and an OpenAI-compatible API key.
- Disk space and time for the Python install: `torch` is a large package.
- No GPU is needed. A normal laptop is enough.

## Installation and setup

1. Clone the repository and enter it:
   ```bash
   git clone https://github.com/Dutta-Pushpa/Flow-Freeze.git
   cd Flow-Freeze
   ```
2. Install the web app dependencies:
   ```bash
   npm install
   ```
3. Create a Python virtual environment and install the model service dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   python3 -m pip install -r requirements.txt
   ```
4. Copy the environment template and edit the values you need:
   ```bash
   cp .env.example .env
   ```
5. Optional: generate fresh synthetic data with the scripts in `data_generator/`. Sample data is already included in `data/`.

## Environment variables

Use placeholders only. Never commit real secrets; `.env` is git-ignored.

| Variable | Purpose | Default or example |
|---|---|---|
| `NODE_ENV` | Node environment | `development` |
| `PORT` | Port for the Node web server | `3000` |
| `DATABASE_URL` | Optional database for audit events and decisions. If it is missing or unreachable, the app falls back to in-memory synthetic demo state | `mysql://user:password@127.0.0.1:3306/flowfreeze` |
| `FLOWFREEZE_LOCAL` | Local-run flag | `true` |
| `PYTHON_API_URL` | Address of the FastAPI model service used by the Node server | `http://127.0.0.1:8000` |
| `FLOWFREEZE_ENABLE_LLM` | Turns on the optional LLM explanation layer | `false` |
| `FLOWFREEZE_LLM_MODEL` | Model name for the LLM layer | `gpt-5-mini` |
| `OPENAI_API_KEY` | Server-side API key, only when the LLM layer is enabled | placeholder, set locally |
| `OPENAI_API_BASE` | Base URL of the OpenAI-compatible API | placeholder, set locally |

## Build commands

```bash
npm run build                          # production build of the React app into dist/
docker build -t flowfreeze .           # web app image
docker build -f Dockerfile.intelligence -t flowfreeze-intelligence .   # model service image
docker compose up                      # PostgreSQL + intelligence service
```

Typical local run (two terminals): start the model service with the `uvicorn` command in "Run the intelligence service", then run `npm run build && npm start` and open `http://localhost:3000`. The web app also works without the Python service, using its deterministic fallback.

## Testing instructions

```bash
python3 -m pytest -q tests         # Python tests (data, graph, taint, fraud model, intervention, API)
npm run check                      # syntax check of the Node server and production build
```

To verify the features manually, follow the Demo story: the recommended hold should be ৳15,000 with about ৳7,000 of legitimate value left outside the action, and the AI / ML page should return a recommendation with a trace ID.

## Other configuration

- `frontend/public/manus-routes.json` lists the app routes for the hosted deployment.
- `.env.example`, `Dockerfile`, `Dockerfile.intelligence` and `docker-compose.yml` hold the deployment and database configuration. Docker Compose reads `OPENAI_API_KEY` and `OPENAI_API_BASE` from your shell if you set them.
- Synthetic datasets and scenarios live in `data/` (`raw/`, `processed/`, `synthetic/`); `docs/` holds the API reference, architecture, data dictionary, model card and responsible-AI notes.
- All data is synthetic. Hold, lien and freeze mechanisms are design assumptions that would need provider-policy, Bangladesh Bank and legal validation before any real deployment. A hold is not a reversal or refund.