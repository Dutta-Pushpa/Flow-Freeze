from fastapi import APIRouter
from backend.services.tracing_service import trace_transactions
from graph.simulator import simulate_flow
router=APIRouter(prefix="/graph",tags=["graph"])
@router.post("/trace")
def trace(payload: dict): return trace_transactions(payload.get("edges",[]),payload.get("source","W4"))
@router.post("/simulate")
def simulate(payload: dict): return simulate_flow(payload.get("edges",[]),payload.get("source","W4"),int(payload.get("delay_minutes",0)),float(payload.get("hold_ratio",68)),float(payload.get("initial_taint",15000)))
