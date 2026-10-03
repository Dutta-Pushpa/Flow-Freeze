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

## Authentication (v0.4)
All `/api/v1/*` routes except `GET /health` require `Authorization: Bearer <token>`. Tokens and roles come from `FLOWFREEZE_API_TOKENS` (`token:role,...`). Missing/unknown token → **401**; role without permission (e.g. `viewer` on `/interventions/recommend`) → **403**. Demo tokens exist only when `FLOWFREEZE_DEMO_MODE=true`.
New: `POST /api/v1/graph/analyze` (fan-in/out, pass-through, cycles, hubs). `/incidents/score` and `/interventions/recommend` now return `explanation` (exact Shapley drivers) and a `narrative` {what_happened, why_risky, what_next}; `confidence` is the calibrated fraud probability and `trace_id` is unique per request.
