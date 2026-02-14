from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import json

# 密码加密上下文 - 使用PBKDF2算法，避免bcrypt的密码长度限制
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger(name)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    # bcrypt算法不允许密码超过72字节，需要截断
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)

def create_access_token(data: Dict[str, Any], secret_key: str, algorithm: str, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def format_response(code: int = 200, message: str = "success", data: Any = None) -> Dict[str, Any]:
    """格式化响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

def format_paginated_response(data: list, total: int, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """格式化分页响应"""
    return {
        "code": 200,
        "message": "success",
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "timestamp": datetime.utcnow().isoformat()
    }

def safe_json_parse(data: str) -> Any:
    """安全解析JSON"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    from email_validator import validate_email as ev_validate, EmailNotValidError
    try:
        ev_validate(email)
        return True
    except EmailNotValidError:
        return False