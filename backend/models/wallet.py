from pydantic import BaseModel
class Wallet(BaseModel):
    wallet_id: str
    balance: float
    account_age_days: int = 30
    transaction_velocity: float = 0
    incoming_amount: float = 0
    outgoing_amount: float = 0
