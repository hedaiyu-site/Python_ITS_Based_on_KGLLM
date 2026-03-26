"""
异常处理模块

定义自定义异常和全局异常处理器
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional


class AppException(Exception):
    """应用基础异常"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class KGConnectionError(AppException):
    """知识图谱连接异常"""
    
    def __init__(self, message: str = "知识图谱连接失败", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class LLMError(AppException):
    """大模型调用异常"""
    
    def __init__(self, message: str = "大模型调用失败", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class ResourceNotFoundError(AppException):
    """资源不存在异常"""
    
    def __init__(self, message: str = "请求的资源不存在", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(AppException):
    """数据验证异常"""
    
    def __init__(self, message: str = "数据验证失败", details: Optional[Dict] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """应用异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "details": {}
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "服务器内部错误",
            "details": str(exc) if settings.DEBUG else {}
        }
    )


from app.core.config import settings
