from fastapi import APIRouter
from backend.models.transaction import Transaction
router=APIRouter(prefix="/transactions",tags=["transactions"])
@router.post("/validate")
def validate(tx: Transaction): return {"ok":True,"transaction":tx.model_dump()}
