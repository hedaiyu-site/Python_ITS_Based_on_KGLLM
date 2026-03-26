"""
测验路由

提供测验功能的API接口
"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from app.services.quiz_service import QuizService
from app.core.dependencies import get_quiz_service, get_current_user_id
from app.api.schemas import (
    QuizQuestionsResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    QuizStatisticsResponse,
    GenerateQuestionsResponse,
    QuizKnowledgePointsResponse
)

router = APIRouter(prefix="/quiz", tags=["测验"])
security = HTTPBearer()


@router.get("/knowledge-points", response_model=QuizKnowledgePointsResponse)
async def get_quiz_knowledge_points(
    user_id: int = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service)
) -> QuizKnowledgePointsResponse:
    """获取用户可测验的知识点列表"""
    knowledge_points = quiz_service.get_quiz_knowledge_points(user_id)
    return QuizKnowledgePointsResponse(
        success=True,
        knowledge_points=knowledge_points
    )


@router.post("/generate/{knowledge_point_id}", response_model=GenerateQuestionsResponse)
async def generate_questions(
    knowledge_point_id: str,
    knowledge_point_name: str,
    count: int = 10,
    user_id: int = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service)
) -> GenerateQuestionsResponse:
    """为知识点生成测验题目"""
    result = quiz_service.generate_and_save_questions(
        knowledge_point_id=knowledge_point_id,
        knowledge_point_name=knowledge_point_name,
        count=count
    )
    return GenerateQuestionsResponse(**result)


@router.get("/questions/{knowledge_point_id}", response_model=QuizQuestionsResponse)
async def get_quiz_questions(
    knowledge_point_id: str,
    count: int = 10,
    user_id: int = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service)
) -> QuizQuestionsResponse:
    """获取知识点的测验题目"""
    questions = quiz_service.get_quiz_questions(knowledge_point_id, count)
    return QuizQuestionsResponse(
        success=True,
        knowledge_point_id=knowledge_point_id,
        questions=questions
    )


@router.post("/submit", response_model=SubmitAnswerResponse)
async def submit_answer(
    request: SubmitAnswerRequest,
    user_id: int = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service)
) -> SubmitAnswerResponse:
    """提交答案并评分"""
    result = quiz_service.submit_answer(
        user_id=user_id,
        knowledge_point_id=request.knowledge_point_id,
        knowledge_point_name=request.knowledge_point_name,
        question_id=request.question_id,
        user_answer=request.user_answer
    )
    return SubmitAnswerResponse(**result)


@router.get("/statistics/{knowledge_point_id}", response_model=QuizStatisticsResponse)
async def get_quiz_statistics(
    knowledge_point_id: str,
    user_id: int = Depends(get_current_user_id),
    quiz_service: QuizService = Depends(get_quiz_service)
) -> QuizStatisticsResponse:
    """获取知识点测验统计"""
    stats = quiz_service.get_quiz_statistics(user_id, knowledge_point_id)
    return QuizStatisticsResponse(**stats)
