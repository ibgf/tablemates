# ✅ backend/api/api_router.py

from fastapi import APIRouter

# 导入各个子模块的路由
from .tickets import router as tickets_router
from .ticket_scan import router as scan_router
from .ticket_refunds import router as refund_router
from .ticket_stats import router as stats_router
from .ticket_discounts import router as discount_router
from .feed import router as feed_router
from .ticketpass import router as ticketpass_router

api_router = APIRouter(prefix="/api")

# 注册各路由模块
api_router.include_router(tickets_router)
api_router.include_router(scan_router)
api_router.include_router(refund_router)
api_router.include_router(stats_router)
api_router.include_router(discount_router)
api_router.include_router(feed_router)
api_router.include_router(ticketpass_router)