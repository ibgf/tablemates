from sqlalchemy import Column, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid

from core.database import Base

class UserFollow(Base):
    __tablename__ = "user_follows"
    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="uq_user_follow"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    followee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())
