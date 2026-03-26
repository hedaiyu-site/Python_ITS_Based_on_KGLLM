"""
API路由模块
"""

from app.api.routers.auth import router as auth_router
from app.api.routers.kg import router as kg_router
from app.api.routers.chat import router as chat_router
from app.api.routers.history import router as history_router
from app.api.routers.learning_path import router as learning_path_router
from app.api.routers.quiz import router as quiz_router

__all__ = ["auth_router", "kg_router", "chat_router", "history_router", "learning_path_router", "quiz_router"]
