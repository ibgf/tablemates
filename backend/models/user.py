from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.core.database import Base
from datetime import datetime
import uuid

# class User(Base):
#     __tablename__ = "users"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     phone = Column(String(20), nullable=True)
#     email = Column(String(100), nullable=True)
#     full_name = Column(String(100), default="游客")
#     avatar = Column(String(255), nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     is_verified = Column(Boolean, default=False)
#     role = Column(String(50), default="guest")

# ✅ 现有的 User 表（不改动）
class User(Base):
    __tablename__ = "users"  # 数据库表名

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String, unique=True, index=True, nullable=True)  # ✅ 手机号可选，但必须唯一
    email = Column(String, unique=True, index=True, nullable=True)  # ✅ 确保 `email` 字段存在
    full_name = Column(String, nullable=True)
    password = Column(String, nullable=False)  # 用户密码（加密存储）
    is_verified = Column(Boolean, default=False)  # 是否已验证手机号，默认未验证
    is_active = Column(Boolean, default=False)  # ✅ 默认未激活 
    verification_code = Column(String, nullable=True)  # ✅ 存验证码
    verification_expires_at = Column(DateTime, nullable=True)  # ✅ 验证码过期时间
    # role = Column(String(20), default=RoleEnum.guest.value)
    role = Column(String(50), default="guest")
        # ✅ 确保 `posts` 关系字段正确定义
    # posts = relationship("Post", back_populates="user")  


class UserAuth(Base):
    __tablename__ = "user_auths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    provider = Column(String(50))  # wechat / google / apple 等
    provider_user_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
