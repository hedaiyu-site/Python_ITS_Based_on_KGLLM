"""
知识图谱路由
"""

from fastapi import APIRouter, Depends

from app.services.kg_service import KnowledgeGraphService
from app.core.dependencies import get_kg_service
from app.core.exceptions import ValidationError
from app.api.schemas import (
    TopicsResponse,
    StatisticsResponse,
    LearningPathResponse,
    CourseOutlineResponse,
    SearchResponse,
    GraphDataResponse
)

router = APIRouter(prefix="/kg", tags=["知识图谱"])


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
) -> StatisticsResponse:
    """获取知识图谱统计信息"""
    stats = kg_service.get_statistics()
    return StatisticsResponse(
        nodes=stats["nodes"],
        relations=stats["relations"]
    )


@router.get("/topics", response_model=TopicsResponse)
async def get_topics(
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
) -> TopicsResponse:
    """获取所有知识点主题"""
    topics = kg_service.get_all_topics()
    return TopicsResponse(topics=topics)


@router.get("/outline/{course_type}", response_model=CourseOutlineResponse)
async def get_outline(
    course_type: str,
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
) -> CourseOutlineResponse:
    """获取课程大纲"""
    if course_type not in ["basic", "advanced"]:
        raise ValidationError(
            message="course_type必须为'basic'或'advanced'",
            details={"course_type": course_type}
        )
    
    outline = kg_service.get_course_outline(course_type)
    return CourseOutlineResponse(
        course=outline.get("course"),
        chapters=outline.get("chapters", [])
    )


@router.get("/path/{topic}", response_model=LearningPathResponse)
async def get_learning_path(
    topic: str,
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
) -> LearningPathResponse:
    """获取特定主题的学习路径"""
    paths = kg_service.get_learning_path(topic)
    return LearningPathResponse(paths=paths)


@router.get("/search/{keyword}", response_model=SearchResponse)
async def search_knowledge(
    keyword: str,
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
) -> SearchResponse:
    """搜索知识点"""
    context = kg_service.search_context(keyword)
    paths = kg_service.get_learning_path(keyword)
    return SearchResponse(
        context=context,
        learning_paths=paths
    )


@router.get("/graph", response_model=GraphDataResponse)
async def get_graph_data(
    course_type: str = None,
    depth: int = 4,
    kg_service: KnowledgeGraphService = Depends(get_kg_service)
) -> GraphDataResponse:
    """
    获取知识图谱可视化数据
    
    参数:
    - course_type: 课程类型 (basic/advanced)，不传则获取全部
    - depth: 层级深度 (1-4)
      - 1: 仅课程
      - 2: 课程+章节
      - 3: 课程+章节+小节
      - 4: 全部层级（包含知识点）
    
    返回:
    - nodes: 节点列表 [{id, name, type, parentId}]
    - edges: 边列表 [{source, target, type}]
    """
    if course_type and course_type not in ["basic", "advanced"]:
        raise ValidationError(
            message="course_type必须为'basic'或'advanced'",
            details={"course_type": course_type}
        )
    
    graph_data = kg_service.get_graph_data(course_type, depth)
    
    return GraphDataResponse(
        success=True,
        nodes=graph_data["nodes"],
        edges=graph_data["edges"]
    )
