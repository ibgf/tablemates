from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


# ✅ 创建票种（请求用）
class TicketTypeCreate(BaseModel):
    # post_id: UUID
    name: str
    price: float
    quantity: int
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    sale_start: Optional[datetime]
    sale_end: Optional[datetime]
    ticket_category: Optional[str]
    user_role: Optional[str]
    is_active: bool = False
    

# ✅ 返回票种信息（响应用）
class TicketTypeOut(BaseModel):
    id: UUID
    post_id: UUID
    name: str
    price: float
    quantity: int
    remaining_quantity: Optional[int] 
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    sale_start: Optional[datetime]
    sale_end: Optional[datetime]
    created_at: datetime
    is_active: bool

    has_registered: Optional[bool] = False 

    model_config = ConfigDict(from_attributes=True)

class TicketTypeToggle(BaseModel):
    activate: bool
