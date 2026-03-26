"""
知识图谱检索模块

提供Neo4j知识图谱的高级检索功能
支持关键词搜索、学习路径获取、相关概念查询等

主要功能:
- 模糊关键词搜索
- 知识上下文获取
- 学习路径查询
- 前置知识获取
- 相关概念查询
- 课程结构获取

依赖:
- neo4j: Neo4j Python驱动

作者: Python学习助手团队
版本: 1.0.0
"""

from neo4j import GraphDatabase
from typing import List, Dict, Optional

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hedaiyu123"
NEO4J_DATABASE = "neo4j"


class KnowledgeGraphRetriever:
    """
    知识图谱检索器
    
    提供各种知识图谱查询功能
    """
    
    def __init__(self):
        """
        初始化检索器
        
        创建Neo4j数据库连接
        """
        self.driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
    
    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        使用全文索引搜索节点
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
        
        Returns:
            匹配的节点列表，包含类型、名称、ID和匹配分数
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                CALL db.index.fulltext.queryNodes('knowledge_index', $keyword)
                YIELD node, score
                RETURN labels(node)[0] as type, node.name as name, node.id as id, score
                ORDER BY score DESC
                LIMIT $limit
            """, keyword=keyword, limit=limit)
            return [dict(record) for record in result]
    
    def search_by_name_fuzzy(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        模糊搜索节点
        
        使用CONTAINS进行模糊匹配
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
        
        Returns:
            匹配的节点列表，包含类型、名称和ID
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (n)
                WHERE n.name CONTAINS $keyword OR n.id CONTAINS $keyword
                RETURN labels(n)[0] as type, n.name as name, n.id as id
                LIMIT $limit
            """, keyword=keyword, limit=limit)
            return [dict(record) for record in result]
    
    def get_knowledge_context(self, keyword: str) -> str:
        """
        获取知识上下文
        
        搜索关键词并返回格式化的知识信息
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            格式化的知识上下文字符串
        """
        nodes = self.search_by_name_fuzzy(keyword, limit=5)
        if not nodes:
            return ""
        
        context_parts = []
        for node in nodes:
            node_info = self.get_node_details(node['id'], node['type'])
            if node_info:
                context_parts.append(node_info)
        
        return "\n\n".join(context_parts)
    
    def get_node_details(self, node_id: str, node_type: str) -> Optional[str]:
        """
        获取节点详细信息
        
        返回节点名称及其所有关系
        
        Args:
            node_id: 节点ID或名称
            node_type: 节点类型
        
        Returns:
            格式化的节点信息字符串
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            if node_type in ['Module', 'DataType', 'Library', 'Tool']:
                result = session.run(f"""
                    MATCH (n:{node_type} {{name: $name}})
                    OPTIONAL MATCH (n)-[r]->(child)
                    RETURN n.name as name, 
                           collect({{relation: type(r), child: child.name}}) as relations
                """, name=node_id)
            else:
                result = session.run(f"""
                    MATCH (n:{node_type} {{id: $id}})
                    OPTIONAL MATCH (n)-[r]->(child)
                    RETURN n.name as name, 
                           collect({{relation: type(r), child: child.name}}) as relations
                """, id=node_id)
            
            record = result.single()
            if not record:
                return None
            
            name = record['name']
            relations = record['relations']
            
            info = f"【{node_type}】{name}\n"
            
            related_items = {}
            for rel in relations:
                if rel['child']:
                    rel_type = rel['relation']
                    if rel_type not in related_items:
                        related_items[rel_type] = []
                    related_items[rel_type].append(rel['child'])
            
            for rel_type, children in related_items.items():
                info += f"  - {rel_type}: {', '.join(children[:5])}"
                if len(children) > 5:
                    info += f" 等{len(children)}项"
                info += "\n"
            
            return info
    
    def get_learning_path(self, topic: str) -> List[Dict]:
        """
        获取特定主题的学习路径
        
        查找包含该主题的课程、章节、小节
        
        Args:
            topic: 学习主题关键词
        
        Returns:
            学习路径列表
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH path = (c:Course)-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_SECTION]->(s:Section)
                WHERE s.name CONTAINS $topic OR ch.name CONTAINS $topic
                RETURN c.name as course, ch.name as chapter, s.name as section
                ORDER BY c.name, ch.id
            """, topic=topic)
            return [dict(record) for record in result]
    
    def get_prerequisites(self, concept: str) -> List[Dict]:
        """
        获取前置知识
        
        查找学习某概念前需要掌握的知识
        
        Args:
            concept: 概念关键词
        
        Returns:
            前置知识列表
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (target)-[:HAS_SUB_POINT|HAS_KNOWLEDGE_POINT*1..3]-(parent)
                WHERE target.name CONTAINS $concept
                RETURN DISTINCT parent.name as prerequisite, labels(parent)[0] as type
                LIMIT 10
            """, concept=concept)
            return [dict(record) for record in result]
    
    def get_related_concepts(self, concept: str) -> List[Dict]:
        """
        获取相关概念
        
        查找与某概念相关的其他概念
        
        Args:
            concept: 概念关键词
        
        Returns:
            相关概念列表
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (n)-[:RELATED_TO|USED_FOR]-(related)
                WHERE n.name CONTAINS $concept
                RETURN related.name as name, labels(related)[0] as type
            """, concept=concept)
            return [dict(record) for record in result]
    
    def get_course_structure(self, course_type: str = "basic") -> Dict:
        """
        获取课程结构
        
        返回指定课程的章节结构
        
        Args:
            course_type: 课程类型('basic'或'advanced')
        
        Returns:
            课程结构字典
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (c:Course {id: $course_id})-[:HAS_CHAPTER]->(ch:Chapter)
                OPTIONAL MATCH (ch)-[:HAS_SECTION]->(s:Section)
                WITH c, ch, collect(s.name) as sections
                ORDER BY ch.id
                RETURN c.name as course, ch.name as chapter, sections
            """, course_id=f"course_{course_type}")
            
            structure = {"course": "", "chapters": []}
            for record in result:
                if not structure["course"]:
                    structure["course"] = record["course"]
                structure["chapters"].append({
                    "chapter": record["chapter"],
                    "sections": record["sections"]
                })
            return structure
    
    def get_all_knowledge_points(self) -> List[str]:
        """
        获取所有知识点名称
        
        Returns:
            所有知识点名称列表
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (n)
                WHERE n.name IS NOT NULL
                RETURN DISTINCT n.name as name
                ORDER BY name
            """)
            return [record['name'] for record in result]
    
    def find_learning_sequence(self, start_topic: str, end_topic: str) -> List[Dict]:
        """
        查找学习序列
        
        找出从起始主题到目标主题的最短学习路径
        
        Args:
            start_topic: 起始主题
            end_topic: 目标主题
        
        Returns:
            学习路径上的节点列表
        """
        with self.driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (start)-[:HAS_SUB_POINT|HAS_KNOWLEDGE_POINT|RELATED_TO*]-(end)
                )
                WHERE start.name CONTAINS $start_topic AND end.name CONTAINS $end_topic
                RETURN [node in nodes(path) | {name: node.name, type: labels(node)[0]}] as path
            """, start_topic=start_topic, end_topic=end_topic)
            record = result.single()
            if record:
                return record['path']
            return []


if __name__ == '__main__':
    """
    主函数
    
    测试知识图谱检索功能
    """
    retriever = KnowledgeGraphRetriever()
    try:
        print("测试知识图谱检索...")
        
        print("\n1. 搜索'列表'相关内容:")
        context = retriever.get_knowledge_context("列表")
        print(context)
        
        print("\n2. 获取'函数'学习路径:")
        path = retriever.get_learning_path("函数")
        for p in path[:3]:
            print(f"  {p['course']} > {p['chapter']} > {p['section']}")
        
        print("\n3. 获取基础课程结构:")
        structure = retriever.get_course_structure("basic")
        print(f"课程: {structure['course']}")
        for ch in structure['chapters'][:3]:
            print(f"  章节: {ch['chapter']}")
        
        print("\n4. 获取相关概念:")
        related = retriever.get_related_concepts("继承")
        for r in related:
            print(f"  {r['type']}: {r['name']}")
        
    finally:
        retriever.close()
