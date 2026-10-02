from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from backend.services.fraud_service import score_incident
router=APIRouter(prefix="/incidents",tags=["incidents"])
@router.post("/score")
def score(req: IncidentRequest): return {"incident_id":req.incident_id,**score_incident(req.reported_amount,req.wallet_balance)}
