#  ✅ 文件路径：schemas/ticket_scan_log.py

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

class TicketScanLogCreate(BaseModel):
    ticket_id: UUID
    scan_type: str = Field(default="in")  # "in" or "out"
    entry_date: datetime
    device_id: Optional[str] = None

class TicketScanLogOut(BaseModel):
    id: UUID
    ticket_id: UUID
    scan_time: datetime
    scan_type: str
    entry_date: datetime
    device_id: Optional[str]

    class Config:
        from_attributes = True
