# backend/models/ticket.py

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, DateTime, Text
from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from uuid import uuid4
from backend.core.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    event_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    ticket_type = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2)) 
    qr_code = Column(Text)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    status = Column(String(20), default="valid")
    created_at = Column(DateTime, default=datetime.utcnow)
