from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.recommendation_service import RecommendationService

router = APIRouter()

# 创建RecommendationService实例
recommendation_service = RecommendationService()

# 个性化推荐相关模型
class RecommendContentRequest(BaseModel):
    user_id: int
    content_type: str = "mixed"
    limit: int = 10

class RecommendationItem(BaseModel):
    item_id: str
    item_type: str
    title: str
    description: str
    relevance_score: float

class RecommendQuestionsRequest(BaseModel):
    user_id: int
    knowledge_node: str
    difficulty: str = "medium"
    limit: int = 5

class UpdatePreferencesRequest(BaseModel):
    preferences: dict

# 路由端点
@router.post("/content", response_model=list[dict])
async def recommend_content(request: RecommendContentRequest):
    """推荐学习内容"""
    results = await recommendation_service.recommend_content(
        request.user_id,
        request.content_type,
        request.limit
    )
    return results

@router.post("/questions", response_model=list[dict])
async def recommend_questions(request: RecommendQuestionsRequest):
    """推荐练习题"""
    results = await recommendation_service.recommend_questions(
        request.user_id,
        request.knowledge_node,
        request.difficulty,
        request.limit
    )
    return results

@router.post("/preferences/update")
async def update_preferences(user_id: int, request: UpdatePreferencesRequest):
    """更新用户偏好"""
    result = await recommendation_service.update_preferences(user_id, request.preferences)
    return result

@router.get("/reasons")
async def get_recommendation_reasons(user_id: int, item_id: str):
    """获取推荐原因"""
    result = await recommendation_service.get_recommendation_reasons(user_id, item_id)
    return result