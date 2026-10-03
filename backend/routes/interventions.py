from fastapi import APIRouter
from backend.models.incident import IncidentRequest
from backend.services.explanation_service import explain_with_rag
from data_generator.config import HOLD_SAFETY_MARGIN
from intervention.recommender import recommend as make_rec
from ml.training import explain_fraud, predict_fraud, predict_next_move
from taint.proportional import proportional_taint
router = APIRouter(prefix="/interventions", tags=["interventions"])

@router.post("/recommend")
def recommend(req: IncidentRequest):
    f = req.to_features(); fraud = predict_fraud(f); move = predict_next_move(f); ex = explain_fraud(f); taint = proportional_taint(req.wallet_balance, req.reported_amount)
    evidence = [*req.evidence, *ex["evidence"]]
    rec = make_rec(req.wallet_balance, taint["tainted_amount"], move["cashout"], evidence, fraud_probability=fraud["fraud_probability"], alert=fraud["alert"], margin=HOLD_SAFETY_MARGIN)
    rec.update(next_move_prediction=move, fraud=fraud, taint=taint)
    return {"recommendation": rec, "explanation": ex, "grounding": explain_with_rag(req.incident_id, evidence, rec, req.model_dump(), [x["text"] for x in ex["factors"]]), "trace_id": rec["trace_id"]}
