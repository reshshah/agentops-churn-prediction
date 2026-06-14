from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class MemberEvent(BaseModel):
    """Core data contract. All agents read from and write to this shape."""

    member_id: str
    tenure_days: int
    renewal_days_remaining: int
    segment: Literal["grocery_heavy", "convenience", "price_sensitive", "mixed"]

    # Behavioral signals
    app_opens_7d: int = Field(ge=0)
    app_opens_30d_baseline: int = Field(ge=0)
    basket_refill_rate: float = Field(ge=0.0, le=1.0)
    session_duration_minutes: float = Field(ge=0.0)
    free_shipping_utilization: float = Field(ge=0.0, le=1.0)
    nudge_skips_30d: int = Field(ge=0)
    category_breadth: int = Field(ge=1)
    pickup_to_delivery_shift: float = Field(ge=0.0)

    generated_at: datetime


class MemberEventBatch(BaseModel):
    members: list[MemberEvent]
    batch_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
