# Security demonstration

The intelligence API exposes `GET /api/v1/security/demo` as a reviewer-friendly, executable demonstration. It checks:

- **Authentication:** the demo analyst token is accepted; an invalid token fails closed.
- **RBAC:** the `analyst` role can view/recommend/record feedback; a `viewer` cannot recommend.
- **Prompt injection:** phrases such as `ignore previous instructions`, `bypass approval`, and `reveal secret` are blocked. Free text is never authoritative for score, amount, scope, or approval.
- **Input validation:** transaction IDs and wallet IDs are constrained, channels are limited to `app|ussd|agent`, and amounts must be finite and positive.
- **Audit integrity:** feedback records are append-only JSONL events with a SHA-256 previous-hash chain.

## Feedback loop

`POST /api/v1/feedback` stores the full chain:

```json
{
  "prediction": "fraud",
  "analyst_decision": "approved",
  "actual_outcome": "fraud",
  "notes": "Confirmed by case review"
}
```

The response includes `stored: true`, `correct: true|false`, the event hash, and the previous hash. `verify_audit_integrity()` detects tampering.

## Graph simulator

`POST /api/v1/graph/simulate` replays timestamped edges through the causal stages:

> delay → transaction replay → money movement → cash-out → recoverable amount

The simulator does not estimate outcomes from `delay × formula`; it replays the supplied graph edges and reports the stage values.
