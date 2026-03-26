"""
学习路径路由

提供学习路径管理的API接口
"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.learning_path_service import LearningPathService
from app.core.dependencies import get_learning_path_service, get_current_user_id
from app.api.schemas import (
    LearningProgressResponse,
    KnowledgePointProgressResponse
)

router = APIRouter(prefix="/learning", tags=["学习路径"])
security = HTTPBearer()


@router.get("/progress", response_model=LearningProgressResponse)
async def get_learning_progress(
    user_id: int = Depends(get_current_user_id),
    learning_path_service: LearningPathService = Depends(get_learning_path_service)
) -> LearningProgressResponse:
    """获取用户学习进度"""
    progress = learning_path_service.get_user_learning_progress(user_id)
    return LearningProgressResponse(**progress)


@router.get("/knowledge/{knowledge_point_id}", response_model=KnowledgePointProgressResponse)
async def get_knowledge_point_detail(
    knowledge_point_id: str,
    user_id: int = Depends(get_current_user_id),
    learning_path_service: LearningPathService = Depends(get_learning_path_service)
) -> KnowledgePointProgressResponse:
    """获取知识点详细进度"""
    detail = learning_path_service.get_knowledge_point_detail(user_id, knowledge_point_id)
    
    if not detail:
        return KnowledgePointProgressResponse(
            success=False,
            message="知识点进度不存在"
        )
    
    return KnowledgePointProgressResponse(
        success=True,
        knowledge_point_id=detail['knowledge_point_id'],
        knowledge_point_name=detail['knowledge_point_name'],
        status=detail['status'],
        mastery_level=detail['mastery_level'],
        quiz_score=detail['quiz_score'],
        quiz_count=detail['quiz_count'],
        correct_count=detail['correct_count'],
        last_study_time=detail['last_study_time']
    )
