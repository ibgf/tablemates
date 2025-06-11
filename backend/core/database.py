# backend/core/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ 自动向上查找 .env 文件
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)

# ✅ 获取数据库连接地址
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ ERROR: DATABASE_URL is not set! Check your .env file.")

# ✅ 创建 SQLAlchemy 引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c client_encoding=utf8"}  # ✅ 这句没有会乱码
)

# ✅ 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ 基类
Base = declarative_base()

# ✅ 明确导入各模型（用于 Base.metadata.create_all 生效）
from backend.models.post import Post
from backend.models.user import User
from backend.models.ticket import Ticket
from backend.models.ticket_type import TicketType
from backend.models.social import PostLike, PostFavorite, UserFollow

# ✅ 可选：初始化时自动创建数据表（开发阶段可保留）
Base.metadata.create_all(bind=engine)

# ✅ 依赖注入函数（FastAPI中使用 Depends(get_db)）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
