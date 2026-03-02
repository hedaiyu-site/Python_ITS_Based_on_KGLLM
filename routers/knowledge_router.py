from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.knowledge_service import KnowledgeService

router = APIRouter()

# 创建KnowledgeService实例
knowledge_service = KnowledgeService()

# 知识图谱相关模型
class KnowledgeNode(BaseModel):
    node_id: str
    node_type: str
    name: str
    content: str
    properties: dict

class KnowledgePath(BaseModel):
    nodes: list[dict]
    relationships: list[dict]

# 路由端点
@router.get("/node/{node_id}", response_model=KnowledgeNode)
async def get_node(node_id: str):
    """根据ID获取知识节点"""
    node = await knowledge_service.get_node(node_id)
    return KnowledgeNode(
        node_id=node["node_id"],
        node_type=node["node_type"],
        name=node["name"],
        content=node["content"],
        properties=node["properties"]
    )

@router.post("/path", response_model=KnowledgePath)
async def get_path(source_id: str, target_id: str):
    """获取两个节点之间的路径"""
    path = await knowledge_service.get_path(source_id, target_id)
    return KnowledgePath(
        nodes=path["nodes"],
        relationships=path["relationships"]
    )

@router.get("/search")
async def search_knowledge(query: str, limit: int = 20):
    """搜索知识图谱"""
    results = await knowledge_service.search(query, limit)
    return {"query": query, "results": results}

@router.get("/related")
async def get_related_nodes(node_id: str, relationship_type: str = None):
    """获取相关节点"""
    nodes = await knowledge_service.get_related_nodes(node_id, relationship_type)
    return {"node_id": node_id, "related_nodes": nodes}

@router.get("/nodes/type")
async def get_nodes_by_type(node_type: str, limit: int = 50):
    """根据类型获取节点"""
    nodes = await knowledge_service.get_nodes_by_type(node_type, limit)
    return {"node_type": node_type, "nodes": nodes}

@router.get("/node/{node_id}/relationships")
async def get_node_relationships(node_id: str):
    """获取节点的所有关系"""
    relationships = await knowledge_service.get_node_relationships(node_id)
    return {"node_id": node_id, "relationships": relationships}