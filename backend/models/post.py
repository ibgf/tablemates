from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from backend.core.database import Base
from datetime import datetime
import uuid


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    post_type = Column(String(50))  # "event", "feed", "news"
    created_at = Column(DateTime, default=datetime.utcnow)
    image_urls = Column(Text)  # 存 JSON 字符串
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    clicks = Column(Integer, default=0)

    # 活动专用字段
    location = Column(String(255))
    max_participants = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    price = Column(Float)
    status = Column(String(50), default="active")
    city = Column(String(100))
    country = Column(String(100))
    is_active = Column(Boolean, default=False)
