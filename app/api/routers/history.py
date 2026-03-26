"""
聊天历史路由

提供聊天历史记录的API接口
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.chat_history_service import ChatHistoryService
from app.core.dependencies import get_chat_history_service, get_current_user_id
from app.api.schemas import (
    ChatHistoryResponse,
    ChatMessageResponse,
    SessionListResponse,
    ChatSessionResponse,
    RecentHistoryResponse,
    DeleteSessionResponse,
    ClearHistoryResponse
)

router = APIRouter(prefix="/history", tags=["聊天历史"])
security = HTTPBearer()


@router.get("/sessions", response_model=SessionListResponse)
async def get_sessions(
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> SessionListResponse:
    """获取用户的所有会话列表"""
    sessions = history_service.get_user_sessions(user_id, limit)
    return SessionListResponse(
        success=True,
        sessions=[ChatSessionResponse(**s) for s in sessions]
    )


@router.get("/session/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> ChatHistoryResponse:
    """获取指定会话的聊天历史"""
    messages = history_service.get_session_history(user_id, session_id, limit)
    return ChatHistoryResponse(
        success=True,
        session_id=session_id,
        messages=[ChatMessageResponse(**m) for m in messages]
    )


@router.get("/recent", response_model=RecentHistoryResponse)
async def get_recent_history(
    limit: int = 10,
    user_id: int = Depends(get_current_user_id),
    history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> RecentHistoryResponse:
    """获取用户最近的聊天记录"""
    messages = history_service.get_recent_history(user_id, limit)
    return RecentHistoryResponse(
        success=True,
        messages=[ChatMessageResponse(**m) for m in messages]
    )


@router.delete("/session/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(
    session_id: str,
    user_id: int = Depends(get_current_user_id),
    history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> DeleteSessionResponse:
    """删除指定会话"""
    success = history_service.delete_session(user_id, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return DeleteSessionResponse(
        success=True,
        message="会话删除成功"
    )


@router.delete("/clear", response_model=ClearHistoryResponse)
async def clear_history(
    user_id: int = Depends(get_current_user_id),
    history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> ClearHistoryResponse:
    """清空用户所有聊天记录"""
    deleted_count = history_service.clear_user_history(user_id)
    return ClearHistoryResponse(
        success=True,
        message="已清空所有聊天记录",
        deleted_count=deleted_count
    )
