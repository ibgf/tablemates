from sqlalchemy import Column, DateTime, ForeignKey, String, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.core.database import Base
import uuid

class TicketRefund(Base):
    __tablename__ = "ticket_refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    refund_amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(Text, nullable=True)

    status = Column(String(20), nullable=False, default="pending")  # pending / approved / rejected
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
