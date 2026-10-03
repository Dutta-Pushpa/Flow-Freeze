from datetime import datetime
from pydantic import BaseModel, Field
class IncidentRequest(BaseModel):
    incident_id: str = Field(min_length=3, max_length=80)
    wallet_id: str = Field(min_length=2, max_length=80)
    reported_amount: float = Field(gt=0, le=10_000_000)
    wallet_balance: float = Field(gt=0, le=10_000_000)
    sender_wallet: str = "reported_sender"
    receiver_wallet: str = "reported_receiver"
    timestamp: datetime | None = None
    transaction_type: str = "transfer"
    channel: str = Field(default="app", pattern=r"^(app|ussd|agent)$")
    sender_velocity: int = Field(default=1, ge=0, le=1000)
    receiver_velocity: int = Field(default=1, ge=0, le=1000)
    cashout_flag: int = Field(default=0, ge=0, le=1)
    new_relationship: int = Field(default=1, ge=0, le=1)
    rapid_forwarding: int = Field(default=0, ge=0, le=1)
    amount_vs_sender_avg: float = Field(default=1.0, gt=0, le=1000)
    hour: int = Field(default=12, ge=0, le=23)
    account_age_days: int = Field(default=365, ge=0, le=10000)
    device_changed: int = Field(default=0, ge=0, le=1)
    merchant_flag: int = Field(default=0, ge=0, le=1)
    evidence: list[str] = Field(default_factory=list, max_length=20)
