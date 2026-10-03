# Responsible AI

| Principle | Implementation |
|---|---|
| Privacy | Synthetic data only; no PII; serving inputs are pseudonymous wallet ids |
| Explainability | Exact Shapley drivers per alert + a What happened / Why risky / What next narrative |
| Fairness | False-alert rate by account age, channel, merchant and legitimate look-alikes; >2× gap is flagged in `evaluation.json` |
| Security | Bearer-token auth (401) + roles (403) on every API route; validated inputs; injection screen on free text; LLM output rejected if it adds numbers not in the structured result; hash-chained audit trail |
| Human oversight | Every recommendation has `requires_human_approval=true`; nothing moves money |
| Transparency | Predictions, assumptions and generated text are separate fields; LLM provider is reported per response |
| No harmful automation | The system recommends; an authorised analyst decides |

## Wrongful-hold risk (the main harm)
A hold on an innocent wallet harms a real person. Controls: hold only the *estimated tainted amount* (+10% margin), never the whole wallet by default; holds expire after 24 h unless a human extends them; the customer is notified where permitted; there is an appeal / re-review path; intermediate wallets are treated as possible victims. Simulation in `data/processed/impact.json` shows how much legitimate value each policy would freeze.
**Regulatory context (to confirm with upay compliance):** AML/CFT suspicious-transaction reporting, Bangladesh Bank MFS rules, and customer-notification rules determine what a hold may lawfully do. This prototype does not encode legal advice.
**Remaining risks:** synthetic-data bias, regex-based injection screening is only one layer, no rate limiting, demo tokens must stay disabled outside local demos.
