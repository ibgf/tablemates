# backend/models/ticket_type.py

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from uuid import uuid4
from backend.core.database import Base

class TicketType(Base):
    __tablename__ = "ticket_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    post_id = Column(UUID, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    # post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    remaining_quantity = Column(Integer, nullable=True)

    sale_start = Column(DateTime, nullable=False)
    sale_end = Column(DateTime, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    ticket_category = Column(String(50), nullable=False)

    is_active = Column(Boolean, default=False, nullable=False)
    limit_per_user = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default="now()")
    user_role = Column(String(50), default="guest")  
