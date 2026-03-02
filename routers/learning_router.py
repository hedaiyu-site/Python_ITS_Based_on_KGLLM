from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.learning_path_service import LearningPathService

router = APIRouter()

# 创建LearningPathService实例
learning_path_service = LearningPathService()

# 学习路径相关模型
class LearningPath(BaseModel):
    path_id: str
    user_id: int
    nodes: list[str]
    progress: dict
    created_at: str

class ProgressUpdate(BaseModel):
    user_id: int
    node_id: str
    mastery_level: float
    completed: bool

# 路由端点
@router.post("/path/generate", response_model=LearningPath)
async def generate_path(user_id: int, target_skill: str):
    """生成个性化学习路径"""
    result = await learning_path_service.generate_path(user_id, target_skill)
    return LearningPath(
        path_id=result["path_id"],
        user_id=result["user_id"],
        nodes=result["nodes"],
        progress=result["progress"],
        created_at=result["created_at"]
    )

@router.post("/progress/update")
async def update_progress(request: ProgressUpdate):
    """更新学习进度"""
    result = await learning_path_service.update_progress(
        request.user_id,
        request.node_id,
        request.mastery_level,
        request.completed
    )
    return {"message": "Progress updated", "data": result}

@router.get("/progress")
async def get_progress(user_id: int, path_id: str):
    """获取学习进度"""
    result = await learning_path_service.get_progress(user_id, path_id)
    return result

@router.post("/path/optimize")
async def optimize_path(user_id: int, path_id: str):
    """优化学习路径"""
    result = await learning_path_service.optimize_path(user_id, path_id)
    return result