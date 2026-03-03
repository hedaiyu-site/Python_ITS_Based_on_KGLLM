from typing import List, Dict, Any, Optional
from data.graph_db import GraphDB
from services.knowledge_vector_service import get_knowledge_vector_service


class KnowledgeService:
    """知识图谱管理服务"""
    
    def __init__(self):
        self.graph_db = GraphDB()
        self.vector_service = get_knowledge_vector_service()
    
    async def get_node(self, node_id: str) -> Dict[str, Any]:
        """根据ID获取知识节点"""
        node = await self.graph_db.get_node(node_id)
        if node:
            return {
                "node_id": node.get("id"),
                "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
                "name": node.get("name"),
                "content": node.get("content"),
                "properties": node.get("properties", {})
            }
        return {
            "node_id": node_id,
            "node_type": "Unknown",
            "name": "",
            "content": "",
            "properties": {}
        }
    
    async def get_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """获取两个节点之间的路径"""
        path = await self.graph_db.get_shortest_path(source_id, target_id)
        return {
            "nodes": path.get("nodes", []),
            "relationships": path.get("relationships", [])
        }
    
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索知识图谱（关键词搜索）"""
        nodes = await self.graph_db.search_nodes(query, limit=limit)
        return [{
            "node_id": node.get("id"),
            "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
            "name": node.get("name"),
            "content": node.get("content"),
            "properties": node.get("properties", {})
        } for node in nodes]
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """语义搜索（基于向量相似度）"""
        try:
            results = await self.vector_service.semantic_search(
                query=query,
                top_k=top_k,
                filters=filters,
                min_score=min_score
            )
            
            formatted_results = []
            for result in results:
                metadata = result.get('metadata', {})
                formatted_results.append({
                    "node_id": metadata.get("node_id"),
                    "node_type": metadata.get("node_type", "Unknown"),
                    "name": metadata.get("name", ""),
                    "content": "",
                    "score": result.get("score", 0),
                    "properties": metadata
                })
            
            return formatted_results
        except Exception as e:
            print(f"语义搜索失败: {e}")
            return []
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """混合搜索（结合关键词和语义搜索）"""
        try:
            results = await self.vector_service.hybrid_search(
                query=query,
                top_k=top_k,
                alpha=alpha
            )
            
            formatted_results = []
            for result in results:
                metadata = result.get('metadata', {})
                formatted_results.append({
                    "node_id": metadata.get("node_id"),
                    "node_type": metadata.get("node_type", "Unknown"),
                    "name": metadata.get("name", ""),
                    "content": "",
                    "score": result.get("score", 0),
                    "properties": metadata
                })
            
            return formatted_results
        except Exception as e:
            print(f"混合搜索失败: {e}")
            return await self.search(query, limit=top_k)
    
    async def get_similar_nodes(self, node_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """获取相似节点（基于向量相似度）"""
        try:
            results = await self.vector_service.get_similar_nodes(node_id, top_k=top_k)
            
            formatted_results = []
            for result in results:
                metadata = result.get('metadata', {})
                formatted_results.append({
                    "node_id": metadata.get("node_id"),
                    "node_type": metadata.get("node_type", "Unknown"),
                    "name": metadata.get("name", ""),
                    "content": "",
                    "score": result.get("score", 0),
                    "properties": metadata
                })
            
            return formatted_results
        except Exception as e:
            print(f"获取相似节点失败: {e}")
            return []
    
    async def get_related_nodes(self, node_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取相关节点"""
        nodes = await self.graph_db.get_related_nodes(node_id, relationship_type)
        return [{
            "node_id": node.get("id"),
            "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
            "name": node.get("name"),
            "content": node.get("content"),
            "relationship_type": node.get("relationship_type"),
            "properties": node.get("properties", {})
        } for node in nodes]
    
    async def get_nodes_by_type(self, node_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """根据类型获取节点"""
        nodes = await self.graph_db.search_nodes("", node_type=node_type, limit=limit)
        return [{
            "node_id": node.get("id"),
            "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
            "name": node.get("name"),
            "content": node.get("content"),
            "properties": node.get("properties", {})
        } for node in nodes]
    
    async def get_node_relationships(self, node_id: str) -> List[Dict[str, Any]]:
        """获取节点的所有关系"""
        related_nodes = await self.graph_db.get_related_nodes(node_id)
        relationships = []
        for node in related_nodes:
            rel_type = node.get("relationship_type")
            if rel_type:
                relationships.append({
                    "target_node_id": node.get("id"),
                    "target_node_name": node.get("name"),
                    "relationship_type": rel_type
                })
        return relationships
    
    async def get_vector_db_stats(self) -> Dict[str, Any]:
        """获取向量数据库统计信息"""
        return await self.vector_service.get_stats()
