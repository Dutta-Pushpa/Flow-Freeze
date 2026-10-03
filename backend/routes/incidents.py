from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from ml.training import predict_fraud, explain_fraud
router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.post("/score")
def score(req: IncidentRequest):
    f = req.to_features(); r = predict_fraud(f)
    return {"incident_id": req.incident_id, **r, "taint_ratio": round(req.reported_amount / max(req.wallet_balance, 1), 4), "explanation": explain_fraud(f)}
