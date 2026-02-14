from typing import Optional, Dict, Any
from datetime import timedelta
from config.settings import settings
from utils.common_utils import verify_password, get_password_hash, create_access_token
from data.user_db import UserDB

class UserService:
    """用户管理服务"""
    
    def __init__(self):
        self.user_db = UserDB()
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        # 获取用户信息
        user = await self.user_db.get_user_by_username(username)
        if not user:
            return {"error": "用户名或密码错误"}
        
        # 验证密码
        if not verify_password(password, user["password_hash"]):
            return {"error": "用户名或密码错误"}
        
        # 生成访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user["id"]), "username": user["username"]},
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            expires_delta=access_token_expires
        )
        
        return {
            "user_id": user["id"],
            "token": access_token,
            "token_type": "bearer",
            "username": user["username"],
            "email": user["email"]
        }
    
    async def register(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = await self.user_db.get_user_by_username(username)
        if existing_user:
            return {"error": "用户名已存在"}
        
        # 哈希密码
        password_hash = get_password_hash(password)
        
        # 创建用户
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash
        }
        created_user = await self.user_db.create_user(user_data)
        
        if created_user:
            return {
                "user_id": created_user["id"],
                "username": created_user["username"],
                "email": created_user["email"]
            }
        return {"error": "注册失败"}
    
    async def get_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户信息"""
        user = await self.user_db.get_user(user_id)
        if user:
            return user
        return {"error": "用户不存在"}
    
    async def update_profile(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户信息"""
        # 检查用户是否存在
        existing_user = await self.user_db.get_user(user_id)
        if not existing_user:
            return {"error": "用户不存在"}
        
        # 更新用户信息
        updated_user = await self.user_db.update_user(user_id, data)
        if updated_user:
            return updated_user
        return {"error": "更新失败"}
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """根据ID获取用户信息"""
        return await self.user_db.get_user(user_id)