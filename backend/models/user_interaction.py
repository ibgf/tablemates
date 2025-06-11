from sqlalchemy import Column, ForeignKey, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from core.database import Base

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    interaction_type = Column(String(50))  # e.g. "like", "comment", "join_game"
    timestamp = Column(DateTime, server_default=func.now())
