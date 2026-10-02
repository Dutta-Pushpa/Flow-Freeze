# FlowFreeze AI/ML demo

1. Generate `python3 -m data_generator.generate_transactions` and scenarios.
2. Start FastAPI with `uvicorn backend.main:app --reload --port 8000`.
3. Call `POST /api/v1/interventions/recommend` for `INC-2407`.
4. Inspect retrieved evidence, structured attribution, confidence, collateral estimate, and `requires_human_approval`.
5. Use the React analyst console to trace the graph, simulate delay/hold size, record a decision, and review the audit event.
6. Send the final analyst outcome to `/api/v1/feedback` for the feedback loop.
