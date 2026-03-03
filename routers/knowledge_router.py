from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.knowledge_service import KnowledgeService

router = APIRouter()

knowledge_service = KnowledgeService()


class KnowledgeNode(BaseModel):
    node_id: str
    node_type: str
    name: str
    content: str
    properties: dict


class KnowledgePath(BaseModel):
    nodes: list[dict]
    relationships: list[dict]


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    min_score: float = 0.3
    filters: Optional[Dict[str, Any]] = None


class HybridSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    alpha: float = 0.5


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
    """搜索知识图谱（关键词搜索）"""
    results = await knowledge_service.search(query, limit)
    return {"query": query, "results": results, "search_type": "keyword"}

@router.post("/search/semantic")
async def semantic_search(request: SemanticSearchRequest):
    """语义搜索（基于向量相似度）"""
    results = await knowledge_service.semantic_search(
        query=request.query,
        top_k=request.top_k,
        min_score=request.min_score,
        filters=request.filters
    )
    return {
        "query": request.query,
        "results": results,
        "search_type": "semantic",
        "total": len(results)
    }

@router.post("/search/hybrid")
async def hybrid_search(request: HybridSearchRequest):
    """混合搜索（结合关键词和语义搜索）"""
    results = await knowledge_service.hybrid_search(
        query=request.query,
        top_k=request.top_k,
        alpha=request.alpha
    )
    return {
        "query": request.query,
        "results": results,
        "search_type": "hybrid",
        "alpha": request.alpha,
        "total": len(results)
    }

@router.get("/related")
async def get_related_nodes(node_id: str, relationship_type: str = None):
    """获取相关节点"""
    nodes = await knowledge_service.get_related_nodes(node_id, relationship_type)
    return {"node_id": node_id, "related_nodes": nodes}

@router.get("/similar")
async def get_similar_nodes(node_id: str, top_k: int = 5):
    """获取相似节点（基于向量相似度）"""
    nodes = await knowledge_service.get_similar_nodes(node_id, top_k)
    return {"node_id": node_id, "similar_nodes": nodes, "total": len(nodes)}

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

@router.get("/vector-db/stats")
async def get_vector_db_stats():
    """获取向量数据库统计信息"""
    stats = await knowledge_service.get_vector_db_stats()
    return {"stats": stats}
