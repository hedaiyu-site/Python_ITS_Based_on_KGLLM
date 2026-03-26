"""
用户业务服务

提供用户注册、登录、认证等业务逻辑
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import logging

from app.repositories.mysql.user_repository import UserRepository
from app.core.config import settings
from app.core.exceptions import ValidationError, AppException

logger = logging.getLogger(__name__)


class UserService:
    """用户业务服务"""
    
    def __init__(self, user_repository: UserRepository, learning_path_service=None):
        self._user_repo = user_repository
        self._learning_path_service = learning_path_service
    
    def register(self, username: str, password: str, email: Optional[str] = None, learning_path: str = "basic") -> Dict[str, Any]:
        """用户注册"""
        if self._user_repo.exists_by_username(username):
            raise ValidationError(message="用户名已存在", details={"username": username})
        
        if email and self._user_repo.exists_by_email(email):
            raise ValidationError(message="邮箱已被注册", details={"email": email})
        
        user_id = self._user_repo.create(username, password, email, learning_path)
        logger.info(f"用户注册成功: {username}, 学习路径: {learning_path}")
        
        if self._learning_path_service:
            try:
                self._learning_path_service.initialize_user_learning_path(user_id, learning_path)
                logger.info(f"初始化用户学习路径成功: user_id={user_id}, path={learning_path}")
            except Exception as e:
                logger.error(f"初始化用户学习路径失败: {e}")
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "learning_path": learning_path,
            "created_at": datetime.now(),
            "is_active": True
        }
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        user = self._user_repo.find_by_username(username)
        
        if not user:
            raise ValidationError(message="用户名或密码错误")
        
        if not user["is_active"]:
            raise ValidationError(message="账户已被禁用")
        
        if user["password"] != password:
            raise ValidationError(message="用户名或密码错误")
        
        token = self._generate_token(user["id"], user["username"])
        logger.info(f"用户登录成功: {username}")
        
        return {
            "access_token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "learning_path": user.get("learning_path", "basic"),
                "created_at": user["created_at"],
                "is_active": user["is_active"]
            }
        }
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        return self._user_repo.find_by_id(user_id)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效的Token: {e}")
            return None
    
    def _generate_token(self, user_id: int, username: str) -> str:
        """生成JWT token"""
        expiration = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": expiration
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
