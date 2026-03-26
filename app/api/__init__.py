"""
表现层模块

包含API路由和数据模型
"""

from app.api.routers import auth_router, kg_router, chat_router, history_router, learning_path_router, quiz_router
from app.api.schemas import *

__all__ = ["auth_router", "kg_router", "chat_router", "history_router", "learning_path_router", "quiz_router"]
