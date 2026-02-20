from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.chat_service import ChatService

router = APIRouter()

# 创建ChatService实例
chat_service = ChatService()

# 对话相关模型
class ChatRequest(BaseModel):
    user_id: int
    question: str
    context: list[dict] = []

class ChatResponse(BaseModel):
    response_id: str
    answer: str
    knowledge_sources: list[str]
    response_time: float

class FeedbackRequest(BaseModel):
    response_id: str
    rating: int
    comment: str = None

# 路由端点
@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """智能问答"""
    result = await chat_service.ask_question(
        user_id=request.user_id,
        question=request.question,
        context=request.context
    )
    return ChatResponse(
        response_id=result["response_id"],
        answer=result["answer"],
        knowledge_sources=result["knowledge_sources"],
        response_time=result["response_time"]
    )

@router.get("/history")
async def get_chat_history(user_id: int, limit: int = 20, offset: int = 0):
    """获取对话历史"""
    return await chat_service.get_history(user_id, limit, offset)

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """提交反馈"""
    return await chat_service.submit_feedback(
        response_id=request.response_id,
        rating=request.rating,
        comment=request.comment
    )

@router.post("/clear")
async def clear_chat_history(user_id: int):
    """清空对话历史"""
    return await chat_service.clear_history(user_id)