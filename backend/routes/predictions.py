from fastapi import APIRouter
from backend.services.prediction_service import predict_next_move
router=APIRouter(prefix="/predictions",tags=["predictions"])
@router.post("/next-move")
def next_move(payload: dict): return predict_next_move(payload.get("features",{}))
