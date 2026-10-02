from pydantic import BaseModel, Field
from datetime import datetime
class Transaction(BaseModel):
    transaction_id: str
    timestamp: datetime
    sender_wallet: str
    receiver_wallet: str
    amount: float = Field(gt=0)
    channel: str = "app"
    is_cashout: bool = False
