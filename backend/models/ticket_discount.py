from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.core.database import Base
import uuid

class TicketDiscount(Base):
    __tablename__ = "ticket_discounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id", ondelete="CASCADE"), nullable=True)

    code = Column(String(50), nullable=True, unique=True)  # 优惠码，可空（公开折扣）
    discount_type = Column(String(20), nullable=False)  # fixed / percentage / minus : fixed 固定价格；percentage 折扣；minus 减免金额
    discount_value = Column(Numeric(10, 2), nullable=False)   # 优惠值（如 10 表示减 10 元，或打 90 折）

    min_price = Column(Numeric(10, 2), nullable=True)  # 满减门槛（可选），满多少才能使用
    usage_limit = Column(Integer, nullable=True)  # 最大使用次数; 限制总使用次数，如前 100 名
    used_count = Column(Integer, default=0)  # 系统记录当前使用次数

    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
