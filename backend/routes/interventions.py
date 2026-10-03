from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from backend.services.intervention_service import recommend_intervention
from backend.services.explanation_service import explain_with_rag
from ml.training import predict_next_move
router=APIRouter(prefix="/interventions",tags=["interventions"])
@router.post("/recommend")
def recommend(req: IncidentRequest):
    move=predict_next_move(req.model_dump())
    rec=recommend_intervention(req.wallet_balance,req.reported_amount,move["cashout"],req.evidence or ["reported flow continuity","cash-out likelihood"]); rec["next_move_prediction"]=move
    return {"recommendation":rec,"grounding":explain_with_rag(req.incident_id,req.evidence,rec)}
