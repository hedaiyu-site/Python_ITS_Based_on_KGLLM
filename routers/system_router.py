from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.system_service import SystemService

router = APIRouter()

# 创建SystemService实例
system_service = SystemService()

# 系统监控相关模型
class SystemStatus(BaseModel):
    status: str
    timestamp: str
    uptime: float
    active_connections: int
    memory_usage: dict
    cpu_usage: float

class MetricsRequest(BaseModel):
    metric_type: str
    start_time: str
    end_time: str
    interval: str = "1m"

# 路由端点
@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    result = await system_service.get_status()
    return SystemStatus(
        status=result["status"],
        timestamp=result["timestamp"],
        uptime=result["uptime"],
        active_connections=result["active_connections"],
        memory_usage=result["memory_usage"],
        cpu_usage=result["cpu_usage"]
    )

@router.post("/metrics")
async def get_system_metrics(request: MetricsRequest):
    """获取系统指标"""
    result = await system_service.get_metrics(
        request.metric_type,
        request.start_time,
        request.end_time,
        request.interval
    )
    return result

@router.get("/health")
async def health_check():
    """健康检查"""
    result = await system_service.get_health_check()
    return result

@router.get("/logs")
async def get_system_logs(log_type: str, limit: int = 100, offset: int = 0):
    """获取系统日志"""
    result = await system_service.get_logs(log_type, limit, offset)
    return result