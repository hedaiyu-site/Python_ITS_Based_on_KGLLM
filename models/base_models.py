from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class BaseResponse(BaseModel):
    """基础响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    code: int = Field(default=200, description="响应码")
    message: str = Field(default="success", description="响应消息")
    data: List[Any] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总条数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页条数")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    level: Optional[str] = Field(default="beginner", description="用户等级")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="用户偏好")

class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, description="密码")

class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[str] = Field(None, description="邮箱")
    level: Optional[str] = Field(None, description="用户等级")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")

class Token(BaseModel):
    """Token模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")

class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")