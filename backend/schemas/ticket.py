from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

# ✅ 返回 Ticket 实例（购票记录 / 详情页）
class TicketOut(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID
    ticket_type: str
    qr_code: Optional[str]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ✅ Ticket + 用户信息组合返回
class TicketWithUserOut(BaseModel):
    ticket_id: UUID
    user_id: UUID
    user_name: Optional[str]
    ticket_type: str
    status: str
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]

class FreeTicketRegisterRequest(BaseModel):
    post_id: UUID
    ticket_type_id: UUID

class FreeTicketCancelRequest(BaseModel):
    post_id: UUID
