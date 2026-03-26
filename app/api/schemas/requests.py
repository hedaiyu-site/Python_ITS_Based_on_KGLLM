"""
请求数据模型
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: Optional[EmailStr] = Field(default=None, description="邮箱")
    learning_path: str = Field(default="basic", description="学习路径: basic, advanced, basic_to_advanced")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class ChatRequest(BaseModel):
    """对话请求"""
    message: str = Field(..., description="用户消息")
    context: Optional[str] = Field(default="", description="可选上下文")
    session_id: Optional[str] = Field(default=None, description="会话ID，不传则创建新会话")


class ChatHistoryRequest(BaseModel):
    """聊天历史请求"""
    session_id: str = Field(..., description="会话ID")
    limit: Optional[int] = Field(default=50, ge=1, le=100, description="返回消息数量限制")
