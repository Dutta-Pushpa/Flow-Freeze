from pydantic import BaseModel
class IncidentRequest(BaseModel):
    incident_id: str
    wallet_id: str
    reported_amount: float
    wallet_balance: float
    evidence: list[str] = []
