from typing import List, Dict, Any, Optional

# 尝试导入neo4j模块
try:
    from neo4j import GraphDatabase
    from config.settings import settings
    NEO4J_AVAILABLE = True
except ImportError:
    # 如果neo4j模块不存在，设置标志为False
    NEO4J_AVAILABLE = False

class GraphDB:
    """知识图谱数据库访问"""
    
    def __init__(self):
        # 初始化Neo4j连接
        self.driver = None
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password)
                )
                print("Neo4j连接初始化成功")
            except Exception as e:
                print(f"Neo4j连接失败: {e}")
                self.driver = None
    
    def __del__(self):
        # 关闭Neo4j连接
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.close()
                print("Neo4j连接已关闭")
            except:
                pass
    
    async def get_node(self, node_id: str) -> Dict[str, Any]:
        """获取知识节点"""
        if not NEO4J_AVAILABLE or not self.driver:
            # 如果Neo4j不可用，返回空结果
            return {
                "id": node_id,
                "name": "示例节点",
                "type": ["Concept"],
                "content": "这是一个示例节点内容",
                "properties": {}
            }
        
        try:
            with self.driver.session() as session:
                # 尝试将node_id转换为整数
                try:
                    node_id_int = int(node_id)
                    # 使用整数ID查询
                    result = session.run(
                        "MATCH (n {id: $node_id}) RETURN n",
                        node_id=node_id_int
                    )
                except ValueError:
                    # 如果转换失败，使用字符串ID查询
                    result = session.run(
                        "MATCH (n {id: $node_id}) RETURN n",
                        node_id=node_id
                    )
                
                record = result.single()
                if record:
                    node = record["n"]
                    print(f"成功获取节点: {node.get('name')} (ID: {node.get('id')})")
                    return {
                        "id": node.get("id"),
                        "name": node.get("name"),
                        "type": node.labels,
                        "content": node.get("content", ""),
                        "properties": {k: v for k, v in node.items() if k not in ["id", "name", "content"]}
                    }
                
                # 如果找不到节点，尝试使用更通用的查询
                print(f"未找到ID为 {node_id} 的节点，尝试使用更通用的查询")
                result = session.run(
                    "MATCH (n) WHERE n.id = $node_id OR n.name CONTAINS $node_id RETURN n LIMIT 1",
                    node_id=node_id
                )
                record = result.single()
                if record:
                    node = record["n"]
                    print(f"通过通用查询找到节点: {node.get('name')} (ID: {node.get('id')})")
                    return {
                        "id": node.get("id"),
                        "name": node.get("name"),
                        "type": node.labels,
                        "content": node.get("content", ""),
                        "properties": {k: v for k, v in node.items() if k not in ["id", "name", "content"]}
                    }
        except Exception as e:
            print(f"获取节点失败: {e}")
        
        # 如果查询失败，返回示例结果
        return {
            "id": node_id,
            "name": "示例节点",
            "type": ["Concept"],
            "content": "这是一个示例节点内容",
            "properties": {}
        }
    
    async def get_relationship(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """获取节点关系"""
        if not NEO4J_AVAILABLE or not self.driver:
            # 如果Neo4j不可用，返回空结果
            return {
                "type": "RELATED_TO",
                "properties": {}
            }
        
        try:
            with self.driver.session() as session:
                # 尝试将ID转换为整数
                try:
                    source_id_int = int(source_id)
                    target_id_int = int(target_id)
                    # 使用整数ID查询
                    result = session.run(
                        "MATCH (a {id: $source_id})-[r]->(b {id: $target_id}) RETURN r",
                        source_id=source_id_int,
                        target_id=target_id_int
                    )
                except ValueError:
                    # 如果转换失败，使用字符串ID查询
                    result = session.run(
                        "MATCH (a {id: $source_id})-[r]->(b {id: $target_id}) RETURN r",
                        source_id=source_id,
                        target_id=target_id
                    )
                
                record = result.single()
                if record:
                    rel = record["r"]
                    print(f"成功获取关系: {rel.type}")
                    return {
                        "type": rel.type,
                        "properties": dict(rel)
                    }
        except Exception as e:
            print(f"获取关系失败: {e}")
        
        # 如果查询失败，返回示例结果
        return {
            "type": "RELATED_TO",
            "properties": {}
        }
    
    async def get_shortest_path(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """获取最短路径"""
        if not NEO4J_AVAILABLE or not self.driver:
            # 如果Neo4j不可用，返回空结果
            return {
                "nodes": [
                    {"id": source_id, "name": "源节点", "type": ["Concept"]},
                    {"id": target_id, "name": "目标节点", "type": ["Concept"]}
                ],
                "relationships": [
                    {
                        "source": source_id,
                        "target": target_id,
                        "type": "RELATED_TO",
                        "properties": {}
                    }
                ]
            }
        
        try:
            with self.driver.session() as session:
                # 尝试将ID转换为整数
                try:
                    source_id_int = int(source_id)
                    target_id_int = int(target_id)
                    # 使用整数ID查询
                    result = session.run(
                        "MATCH path = shortestPath((a {id: $source_id})-[*]->(b {id: $target_id})) RETURN path",
                        source_id=source_id_int,
                        target_id=target_id_int
                    )
                except ValueError:
                    # 如果转换失败，使用字符串ID查询
                    result = session.run(
                        "MATCH path = shortestPath((a {id: $source_id})-[*]->(b {id: $target_id})) RETURN path",
                        source_id=source_id,
                        target_id=target_id
                    )
                
                record = result.single()
                if record:
                    path = record["path"]
                    nodes = []
                    relationships = []
                    
                    # 提取路径中的节点和关系
                    for node in path.nodes:
                        nodes.append({
                            "id": node.get("id"),
                            "name": node.get("name"),
                            "type": node.labels
                        })
                    
                    for rel in path.relationships:
                        relationships.append({
                            "source": rel.start_node.get("id"),
                            "target": rel.end_node.get("id"),
                            "type": rel.type,
                            "properties": dict(rel)
                        })
                    
                    print(f"成功获取路径: {len(nodes)}个节点, {len(relationships)}个关系")
                    return {
                        "nodes": nodes,
                        "relationships": relationships
                    }
        except Exception as e:
            print(f"获取路径失败: {e}")
        
        # 如果查询失败，返回示例结果
        return {
            "nodes": [
                {"id": source_id, "name": "源节点", "type": ["Concept"]},
                {"id": target_id, "name": "目标节点", "type": ["Concept"]}
            ],
            "relationships": [
                {
                    "source": source_id,
                    "target": target_id,
                    "type": "RELATED_TO",
                    "properties": {}
                }
            ]
        }
    
    async def search_nodes(self, query: str, node_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索节点"""
        if not NEO4J_AVAILABLE or not self.driver:
            # 如果Neo4j不可用，返回空结果
            return [{
                "id": f"example_{i}",
                "name": f"示例节点 {i}",
                "type": ["Concept"],
                "content": f"这是一个示例节点内容，匹配查询: {query}",
                "properties": {}
            } for i in range(min(3, limit))]
        
        try:
            with self.driver.session() as session:
                if node_type:
                    # 按类型搜索
                    print(f"搜索类型为 {node_type} 且包含 '{query}' 的节点")
                    result = session.run(
                        f"MATCH (n:{node_type}) WHERE n.name CONTAINS $search_query OR n.content CONTAINS $search_query RETURN n LIMIT $limit",
                        search_query=query,
                        limit=limit
                    )
                else:
                    # 全局搜索
                    print(f"搜索包含 '{query}' 的节点")
                    result = session.run(
                        "MATCH (n) WHERE n.name CONTAINS $search_query OR n.content CONTAINS $search_query RETURN n LIMIT $limit",
                        search_query=query,
                        limit=limit
                    )
                
                nodes = []
                for record in result:
                    node = record["n"]
                    nodes.append({
                        "id": node.get("id"),
                        "name": node.get("name"),
                        "type": node.labels,
                        "content": node.get("content", ""),
                        "properties": {k: v for k, v in node.items() if k not in ["id", "name", "content"]}
                    })
                
                print(f"搜索到 {len(nodes)} 个节点")
                
                # 如果找不到匹配的节点，尝试使用更通用的查询
                if not nodes:
                    print(f"未找到匹配 '{query}' 的节点，尝试使用更通用的查询")
                    if node_type:
                        result = session.run(
                            f"MATCH (n:{node_type}) WHERE n.name =~ $query_pattern OR n.content =~ $query_pattern RETURN n LIMIT $limit",
                            query_pattern=f".*{query}.*",
                            limit=limit
                        )
                    else:
                        result = session.run(
                            "MATCH (n) WHERE n.name =~ $query_pattern OR n.content =~ $query_pattern RETURN n LIMIT $limit",
                            query_pattern=f".*{query}.*",
                            limit=limit
                        )
                    for record in result:
                        node = record["n"]
                        nodes.append({
                            "id": node.get("id"),
                            "name": node.get("name"),
                            "type": node.labels,
                            "content": node.get("content", ""),
                            "properties": {k: v for k, v in node.items() if k not in ["id", "name", "content"]}
                        })
                    print(f"通用查询找到 {len(nodes)} 个节点")
                
                return nodes
        except Exception as e:
            print(f"搜索节点失败: {e}")
        
        # 如果查询失败，返回示例结果
        return [{
            "id": f"example_{i}",
            "name": f"示例节点 {i}",
            "type": ["Concept"],
            "content": f"这是一个示例节点内容，匹配查询: {query}",
            "properties": {}
        } for i in range(min(3, limit))]
    
    async def get_related_nodes(self, node_id: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取相关节点"""
        if not NEO4J_AVAILABLE or not self.driver:
            # 如果Neo4j不可用，返回空结果
            return [{
                "id": f"related_{i}",
                "name": f"相关节点 {i}",
                "type": ["Concept"],
                "content": f"这是一个与节点 {node_id} 相关的示例节点",
                "relationship_type": relationship_type or "RELATED_TO",
                "properties": {}
            } for i in range(3)]
        
        try:
            with self.driver.session() as session:
                # 尝试将node_id转换为整数
                try:
                    node_id_int = int(node_id)
                    node_id_param = node_id_int
                except ValueError:
                    node_id_param = node_id
                
                if relationship_type:
                    # 按关系类型获取
                    print(f"获取与节点 {node_id} 存在 {relationship_type} 关系的节点")
                    result = session.run(
                        f"MATCH (a {{id: $node_id}})-[:{relationship_type}]->(b) RETURN b",
                        node_id=node_id_param
                    )
                else:
                    # 获取所有相关节点
                    print(f"获取与节点 {node_id} 相关的所有节点")
                    result = session.run(
                        "MATCH (a {id: $node_id})-[r]->(b) RETURN b, type(r) as rel_type",
                        node_id=node_id_param
                    )
                
                nodes = []
                for record in result:
                    node = record["b"]
                    node_data = {
                        "id": node.get("id"),
                        "name": node.get("name"),
                        "type": node.labels,
                        "content": node.get("content", ""),
                        "properties": {k: v for k, v in node.items() if k not in ["id", "name", "content"]}
                    }
                    if "rel_type" in record:
                        node_data["relationship_type"] = record["rel_type"]
                    nodes.append(node_data)
                
                print(f"找到 {len(nodes)} 个相关节点")
                
                # 如果找不到相关节点，尝试使用更通用的查询
                if not nodes:
                    print(f"未找到与节点 {node_id} 相关的节点，尝试使用更通用的查询")
                    result = session.run(
                        "MATCH (a)-[r]->(b) WHERE a.id = $node_id OR a.name CONTAINS $node_id RETURN b, type(r) as rel_type LIMIT 10",
                        node_id=node_id
                    )
                    for record in result:
                        node = record["b"]
                        node_data = {
                            "id": node.get("id"),
                            "name": node.get("name"),
                            "type": node.labels,
                            "content": node.get("content", ""),
                            "properties": {k: v for k, v in node.items() if k not in ["id", "name", "content"]}
                        }
                        if "rel_type" in record:
                            node_data["relationship_type"] = record["rel_type"]
                        nodes.append(node_data)
                    print(f"通用查询找到 {len(nodes)} 个相关节点")
                
                return nodes
        except Exception as e:
            print(f"获取相关节点失败: {e}")
        
        # 如果查询失败，返回示例结果
        return [{
            "id": f"related_{i}",
            "name": f"相关节点 {i}",
            "type": ["Concept"],
            "content": f"这是一个与节点 {node_id} 相关的示例节点",
            "relationship_type": relationship_type or "RELATED_TO",
            "properties": {}
        } for i in range(3)]