from sqlalchemy import Column, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid

from core.database import Base

class Friend(Base):
    __tablename__ = "friends"
    __table_args__ = (UniqueConstraint("user_id", "friend_id", name="uq_friendship"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    friend_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())
