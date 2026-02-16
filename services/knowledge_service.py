from typing import List, Dict, Any, Optional
from data.graph_db import GraphDB

class KnowledgeService:
    """知识图谱管理服务"""
    
    def __init__(self):
        # 初始化知识图谱数据库访问
        self.graph_db = GraphDB()
    
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
        """搜索知识图谱"""
        nodes = await self.graph_db.search_nodes(query, limit=limit)
        return [{
            "node_id": node.get("id"),
            "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
            "name": node.get("name"),
            "content": node.get("content"),
            "properties": node.get("properties", {})
        } for node in nodes]
    
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