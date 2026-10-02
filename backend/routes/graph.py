from fastapi import APIRouter
from backend.services.tracing_service import trace_transactions
router=APIRouter(prefix="/graph",tags=["graph"])
@router.post("/trace")
def trace(payload: dict): return trace_transactions(payload.get("edges",[]),payload.get("source","W4"))
