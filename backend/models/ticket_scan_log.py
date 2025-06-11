from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.core.database import Base
import uuid

class TicketScanLog(Base):
    __tablename__ = "ticket_scan_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    scan_time = Column(DateTime, server_default=func.now(), nullable=False)
    scan_type = Column(String(10), default="in")  # 可为 "in" 或 "out"
    entry_date = Column(DateTime, nullable=False)
    device_id = Column(String, nullable=True)  # 记录终端或闸机编号
