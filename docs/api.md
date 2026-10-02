# FlowFreeze API contract

FastAPI model service runs with `uvicorn backend.main:app --port 8000`.

| Endpoint | Purpose |
|---|---|
| `GET /health` | pipeline, model-stack, and decision-boundary health |
| `POST /api/v1/incidents/score` | structured risk score and feature attribution |
| `POST /api/v1/transactions/validate` | validate incoming transaction contract |
| `POST /api/v1/graph/trace` | downstream trace and cash-out points |
| `POST /api/v1/predictions/next-move` | forward/cash-out/other probabilities |
| `POST /api/v1/interventions/recommend` | proportionate recommendation plus retrieved grounding |
| `POST /api/v1/feedback` | analyst outcome and label feedback loop |

Every recommendation carries `trace_id`, `confidence`, `collateral_estimate`, `requires_human_approval`, and structured evidence.
