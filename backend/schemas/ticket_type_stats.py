#  ✅ 文件路径：schemas/ticket_type_stats.py

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class TicketTypeStatsOut(BaseModel):
    id: UUID
    ticket_type_id: UUID
    total_quantity: int
    sold_quantity: int
    checked_in_count: int
    refund_quantity: int
    updated_at: datetime

    class Config:
        from_attributes = True
