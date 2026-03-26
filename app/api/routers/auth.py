"""
用户认证路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.user_service import UserService
from app.core.dependencies import get_user_service
from app.api.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    LoginResponse,
    RegisterResponse
)

router = APIRouter(prefix="/auth", tags=["用户认证"])
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    user_service: UserService = Depends(get_user_service)
) -> RegisterResponse:
    """用户注册"""
    user = user_service.register(
        username=request.username,
        password=request.password,
        email=request.email,
        learning_path=request.learning_path
    )
    return RegisterResponse(
        message="注册成功",
        user=UserResponse(**user)
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: UserLoginRequest,
    user_service: UserService = Depends(get_user_service)
) -> LoginResponse:
    """用户登录"""
    result = user_service.login(
        username=request.username,
        password=request.password
    )
    return LoginResponse(
        access_token=result["access_token"],
        user=UserResponse(**result["user"])
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """获取当前用户信息"""
    token = credentials.credentials
    payload = user_service.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的token"
        )
    
    user = user_service.get_user_by_id(payload["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse(**user)
