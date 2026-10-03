from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from backend.services.intervention_service import recommend_intervention
from backend.services.explanation_service import explain_with_rag
from ml.training import predict_next_move
router=APIRouter(prefix="/interventions",tags=["interventions"])
@router.post("/recommend")
def recommend(req: IncidentRequest):
    move=predict_next_move({"amount":req.reported_amount,"sender_velocity":5,"receiver_velocity":4,"hop_count":2,"cashout_flag":1,"new_relationship":1,"account_age_days":19,"channel":"app","merchant_flag":0})
    rec=recommend_intervention(req.wallet_balance,req.reported_amount,move["cashout"],req.evidence or ["reported flow continuity","cash-out likelihood"])
    rec["next_move_prediction"]=move
    return {"recommendation":rec,"grounding":explain_with_rag(req.incident_id,req.evidence,rec)}
