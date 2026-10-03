from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from backend.services.fraud_service import score_transaction
router=APIRouter(prefix="/incidents",tags=["incidents"])
@router.post("/score")
def score(req: IncidentRequest):
    transaction=req.model_dump(exclude={"incident_id","wallet_id","wallet_balance","evidence"}); transaction["amount_bdt"]=req.reported_amount
    return {"incident_id":req.incident_id,**score_transaction(transaction),"taint_ratio":round(req.reported_amount/max(req.wallet_balance,1),4)}
