from sqlalchemy import Column, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from backend.core.database import Base
from datetime import datetime
import uuid

class PostLike(Base):
    __tablename__ = "post_likes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)


class PostFavorite(Base):
    __tablename__ = "post_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_favorite"),
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, server_default=func.now())


class UserFollow(Base):
    __tablename__ = "user_follows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    followed_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
