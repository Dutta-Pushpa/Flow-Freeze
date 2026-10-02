# Backend route ownership

The executable route registry lives in `backend/main.js` so the prototype can be started with one portable Node entrypoint. These route groups are kept as domain modules in the full structure:

- incidents: incident list/detail and risk evidence
- transactions: transaction and graph data
- graph: tracing and cash-out points
- predictions: next-move probabilities
- interventions: recommendation and analyst decisions

Each endpoint is deterministic and synthetic by default. The managed MySQL adapter persists intervention decisions and audit events when `DATABASE_URL` is available.
