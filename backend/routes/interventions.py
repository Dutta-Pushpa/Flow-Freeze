from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from backend.services.intervention_service import recommend_intervention
from backend.services.explanation_service import explain_with_rag
router=APIRouter(prefix="/interventions",tags=["interventions"])
@router.post("/recommend")
def recommend(req: IncidentRequest):
    rec=recommend_intervention(req.wallet_balance,req.reported_amount,.81,req.evidence or ["reported flow continuity","cash-out likelihood"])
    return {"recommendation":rec,"grounding":explain_with_rag(req.incident_id,req.evidence,rec)}
