from pydantic import BaseModel
class InterventionDecision(BaseModel):
    decision: str
    reason: str
    amount: float
class InterventionRecommendation(BaseModel):
    amount: float
    scope: str
    rationale: str
    confidence: float
    collateral_estimate: float
    requires_human_approval: bool = True
    trace_id: str
