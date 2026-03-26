"""
Python学习助手API主入口

基于FastAPI框架实现的Python学习助手后端API服务
提供知识图谱查询、大模型对话、学习路径推荐等功能

架构:
- 表现层(api): API路由和数据模型
- 业务逻辑层(services): 业务服务
- 数据层(repositories): 数据仓库
- AI服务层(ai): 大模型等AI服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler
)
from app.core.dependencies import get_kg_repository, get_chat_history_repository
from app.api.routers.auth import router as auth_router
from app.api.routers.kg import router as kg_router
from app.api.routers.chat import router as chat_router
from app.api.routers.history import router as history_router
from app.api.routers.learning_path import router as learning_path_router
from app.api.routers.quiz import router as quiz_router
from app.api.schemas.responses import HealthResponse

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("应用启动中...")
    kg_repo = get_kg_repository()
    get_chat_history_repository()
    yield
    logger.info("应用关闭中...")
    kg_repo.close()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(auth_router, prefix="/api")
app.include_router(kg_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(learning_path_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")


@app.get("/", tags=["根路径"])
async def root():
    """API根路径"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["健康检查"])
async def health_check() -> HealthResponse:
    """健康检查接口"""
    return HealthResponse(status="healthy", version=settings.APP_VERSION)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
