from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os

# 本地模块导入
from backend.core.database import engine, Base, get_db
from backend.models.post import Post
from backend.services.image_utils import to_thumbnail_urls
from backend.models.ticket import Ticket
from backend.models.ticket_type import TicketType  # ✅ 确保导入新模型

# 路由模块（重构后的新结构）
from backend.api.users import router as users_router
from backend.api.posts import router as posts_router
from backend.api.social import router as social_router
from backend.api.uploads import router as uploads_router
from backend.api.api_router import api_router
from backend.api import organizer


# 初始化数据库表结构
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI(title="TableMates API", version="1.0")

# 配置静态资源目录
static_dir = os.path.join(os.getcwd(), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册各功能模块路由
app.include_router(users_router, prefix="/auth")
app.include_router(posts_router, prefix="/api/posts")
app.include_router(social_router, prefix="/api")
app.include_router(uploads_router, prefix="/api/uploads")
app.include_router(api_router)
app.include_router(organizer.router, prefix="/api/organizer", tags=["Organizer"])

# ✅ 测试接口
@app.get("/")
def read_root():
    return {"message": "TableMates API is running 🚀"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    return {"message": "Database connection successful 🎉"}
