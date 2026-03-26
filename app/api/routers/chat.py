"""
对话路由
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json

from app.services.chat_service import ChatService
from app.core.dependencies import get_chat_service, get_current_user_id
from app.api.schemas import ChatRequest

router = APIRouter(prefix="/chat", tags=["对话"])
security = HTTPBearer()


@router.post("")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_service: ChatService = Depends(get_chat_service)
) -> StreamingResponse:
    """流式对话接口"""
    stream_generator, session_id = await chat_service.chat_stream(
        message=request.message, 
        context=request.context or "",
        user_id=user_id,
        session_id=request.session_id
    )
    
    async def generate():
        yield f"data: {json.dumps({'session_id': session_id}, ensure_ascii=False)}\n\n"
        async for chunk in stream_generator:
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
