#  ✅ 文件路径：schemas/ticket_refund.py

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class TicketRefundCreate(BaseModel):
    ticket_id: UUID
    user_id: UUID
    refund_amount: float
    reason: Optional[str] = None

class TicketRefundReview(BaseModel):
    reviewed_by: UUID
    status: str = Field(..., pattern="^(approved|rejected)$")

class TicketRefundOut(BaseModel):
    id: UUID
    ticket_id: UUID
    user_id: UUID
    refund_amount: float
    reason: Optional[str]
    status: str
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
