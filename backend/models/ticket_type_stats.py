from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.core.database import Base
import uuid

class TicketTypeStats(Base):
    __tablename__ = "ticket_type_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id", ondelete="CASCADE"), nullable=False, unique=True)

    total_quantity = Column(Integer, nullable=False, default=0)       # 创建票种时总数
    sold_quantity = Column(Integer, nullable=False, default=0)        # 已售出
    checked_in_count = Column(Integer, nullable=False, default=0)     # 扫码入场数
    refund_quantity = Column(Integer, nullable=False, default=0)      # 退票数

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
