import asyncio
from typing import List, Dict, Any, Optional
from data.vector_db import VectorDB, get_vector_db
from data.graph_db import GraphDB
from ai_services.llm_service import LLMService


class KnowledgeVectorService:
    """知识向量化服务"""
    
    def __init__(self):
        self.vector_db = get_vector_db()
        self.graph_db = GraphDB()
        self.llm_service = LLMService()
        self.batch_size = 20
    
    async def vectorize_knowledge_graph(
        self,
        node_types: Optional[List[str]] = None,
        batch_size: int = 20
    ) -> Dict[str, Any]:
        if node_types is None:
            node_types = ["Concept", "Topic", "Subtopic", "Example", "Operator", 
                         "ControlStructure", "Keyword", "Function", "Module"]
        
        self.batch_size = batch_size
        total_vectorized = 0
        errors = []
        
        for node_type in node_types:
            try:
                print(f"正在处理节点类型: {node_type}")
                count = await self._vectorize_nodes_by_type(node_type)
                total_vectorized += count
                print(f"节点类型 {node_type} 向量化完成，共 {count} 个节点")
            except Exception as e:
                error_msg = f"向量化节点类型 {node_type} 失败: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
        
        self.vector_db.save_to_disk()
        
        stats = self.vector_db.get_stats()
        
        return {
            "total_vectorized": total_vectorized,
            "errors": errors,
            "stats": stats
        }
    
    async def _vectorize_nodes_by_type(self, node_type: str) -> int:
        nodes = await self.graph_db.search_nodes("", node_type=node_type, limit=1000)
        
        if not nodes:
            return 0
        
        total_count = 0
        
        for i in range(0, len(nodes), self.batch_size):
            batch = nodes[i:i + self.batch_size]
            
            texts = []
            metadata_list = []
            
            for node in batch:
                text = self._create_node_text(node)
                texts.append(text)
                
                metadata = {
                    "node_id": node.get("id"),
                    "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
                    "name": node.get("name", ""),
                    "source": node.get("properties", {}).get("source", "")
                }
                metadata_list.append(metadata)
            
            try:
                embeddings = await self.llm_service.batch_embedding(texts)
                
                valid_embeddings = []
                valid_metadata = []
                for emb, meta in zip(embeddings, metadata_list):
                    if emb and not all(v == 0 for v in emb):
                        valid_embeddings.append(emb)
                        valid_metadata.append(meta)
                
                if valid_embeddings:
                    result = await self.vector_db.insert_vectors(valid_embeddings, valid_metadata)
                    total_count += result.get("inserted_count", 0)
                
                print(f"批次 {i // self.batch_size + 1} 完成，已向量化 {total_count} 个节点")
                
            except Exception as e:
                print(f"批次 {i // self.batch_size + 1} 向量化失败: {e}")
            
            await asyncio.sleep(0.5)
        
        return total_count
    
    def _create_node_text(self, node: Dict[str, Any]) -> str:
        parts = []
        
        name = node.get("name", "")
        if name:
            parts.append(f"名称: {name}")
        
        node_type = list(node.get("type", []))[0] if node.get("type") else "Unknown"
        parts.append(f"类型: {node_type}")
        
        content = node.get("content", "")
        if content:
            parts.append(f"内容: {content}")
        
        properties = node.get("properties", {})
        if properties:
            for key, value in properties.items():
                if value and key not in ["id", "name", "content"]:
                    parts.append(f"{key}: {value}")
        
        return "\n".join(parts)
    
    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        query_embedding = await self.llm_service.embedding(query)
        
        if not query_embedding or all(v == 0 for v in query_embedding):
            print("生成查询向量失败")
            return []
        
        results = await self.vector_db.search(
            query_vector=query_embedding,
            top_k=top_k,
            filters=filters,
            min_score=min_score
        )
        
        return results
    
    async def get_similar_nodes(
        self,
        node_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        node = await self.graph_db.get_node(node_id)
        
        if not node:
            return []
        
        text = self._create_node_text(node)
        embedding = await self.llm_service.embedding(text)
        
        if not embedding or all(v == 0 for v in embedding):
            return []
        
        filters = {"node_id": node_id}
        results = await self.vector_db.search(
            query_vector=embedding,
            top_k=top_k + 1,
            min_score=0.5
        )
        
        filtered_results = [r for r in results if r.get("metadata", {}).get("node_id") != node_id]
        
        return filtered_results[:top_k]
    
    async def update_node_vector(self, node_id: str) -> bool:
        try:
            node = await self.graph_db.get_node(node_id)
            
            if not node:
                return False
            
            text = self._create_node_text(node)
            embedding = await self.llm_service.embedding(text)
            
            if not embedding or all(v == 0 for v in embedding):
                return False
            
            metadata = {
                "node_id": node.get("id"),
                "node_type": list(node.get("type", []))[0] if node.get("type") else "Unknown",
                "name": node.get("name", ""),
                "source": node.get("properties", {}).get("source", "")
            }
            
            result = await self.vector_db.insert_vectors([embedding], [metadata])
            
            self.vector_db.save_to_disk()
            
            return result.get("inserted_count", 0) > 0
        except Exception as e:
            print(f"更新节点向量失败: {e}")
            return False
    
    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        vector_results = await self.semantic_search(query, top_k=top_k * 2)
        
        graph_results = await self.graph_db.search_nodes(query, limit=top_k * 2)
        
        vector_scores = {}
        for i, result in enumerate(vector_results):
            node_id = result.get("metadata", {}).get("node_id")
            if node_id:
                vector_scores[str(node_id)] = {
                    "score": result.get("score", 0) * alpha,
                    "metadata": result.get("metadata", {}),
                    "source": "vector"
                }
        
        graph_scores = {}
        for i, node in enumerate(graph_results):
            node_id = node.get("id")
            if node_id:
                graph_score = (1 - alpha) * (1 - i / len(graph_results)) if graph_results else 0
                graph_scores[str(node_id)] = {
                    "score": graph_score,
                    "node": node,
                    "source": "graph"
                }
        
        combined_results = {}
        
        for node_id, data in vector_scores.items():
            if node_id not in combined_results:
                combined_results[node_id] = {"score": 0, "metadata": None}
            combined_results[node_id]["score"] += data["score"]
            combined_results[node_id]["metadata"] = data["metadata"]
        
        for node_id, data in graph_scores.items():
            if node_id not in combined_results:
                combined_results[node_id] = {"score": 0, "metadata": None}
            combined_results[node_id]["score"] += data["score"]
            if not combined_results[node_id]["metadata"]:
                combined_results[node_id]["metadata"] = {
                    "node_id": node_id,
                    "node_type": list(data["node"].get("type", []))[0] if data["node"].get("type") else "Unknown",
                    "name": data["node"].get("name", "")
                }
        
        sorted_results = sorted(
            combined_results.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        return [
            {
                "node_id": node_id,
                "score": data["score"],
                "metadata": data["metadata"]
            }
            for node_id, data in sorted_results[:top_k]
        ]
    
    async def get_stats(self) -> Dict[str, Any]:
        return self.vector_db.get_stats()
    
    async def clear_all_vectors(self) -> bool:
        result = await self.vector_db.clear_all()
        if result:
            self.vector_db.save_to_disk()
        return result


knowledge_vector_service = None

def get_knowledge_vector_service() -> KnowledgeVectorService:
    global knowledge_vector_service
    if knowledge_vector_service is None:
        knowledge_vector_service = KnowledgeVectorService()
    return knowledge_vector_service
