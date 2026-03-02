from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.user_service import UserService

router = APIRouter()

# 创建UserService实例
user_service = UserService()

# 基本请求响应模型
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class UserProfile(BaseModel):
    user_id: int
    username: str
    email: str
    level: str
    preferences: dict

class UpdateProfileRequest(BaseModel):
    email: str = None
    level: str = None
    preferences: dict = None

# 路由端点
@router.post("/login")
async def login(request: LoginRequest):
    """用户登录"""
    result = await user_service.login(request.username, request.password)
    return result

@router.post("/register")
async def register(request: RegisterRequest):
    """用户注册"""
    result = await user_service.register(request.username, request.password, request.email)
    return result

@router.get("/profile", response_model=UserProfile)
async def get_profile(user_id: int):
    """获取用户信息"""
    result = await user_service.get_profile(user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return UserProfile(
        user_id=result["id"],
        username=result["username"],
        email=result["email"],
        level=result["level"],
        preferences=result["preferences"]
    )

@router.put("/profile")
async def update_profile(user_id: int, request: UpdateProfileRequest):
    """更新用户信息"""
    update_data = {}
    if request.email is not None:
        update_data["email"] = request.email
    if request.level is not None:
        update_data["level"] = request.level
    if request.preferences is not None:
        update_data["preferences"] = request.preferences
    
    result = await user_service.update_profile(user_id, update_data)
    return result