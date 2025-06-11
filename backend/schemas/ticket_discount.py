#  ✅ 文件路径：schemas/ticket_discount.py

from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class TicketDiscountCreate(BaseModel):
    event_id: Optional[UUID]
    ticket_type_id: Optional[UUID]
    code: Optional[str]
    discount_type: str  # fixed / percentage / minus
    discount_value: float
    min_price: Optional[float] = None
    usage_limit: Optional[int] = None
    valid_from: datetime
    valid_until: datetime

class TicketDiscountOut(BaseModel):
    id: UUID
    event_id: Optional[UUID]
    ticket_type_id: Optional[UUID]
    code: Optional[str]
    discount_type: str
    discount_value: float
    min_price: Optional[float]
    usage_limit: Optional[int]
    used_count: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool

    class Config:
        from_attributes = True
