"""
知识图谱数据仓库

提供Neo4j知识图谱的数据库操作
"""

from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphRepository:
    """
    知识图谱数据仓库
    
    负责知识图谱数据的查询操作
    """
    
    def __init__(self, url: str, user: str, password: str, database: str = "neo4j"):
        self._url = url
        self._user = user
        self._password = password
        self._database = database
        self._driver = None
        self._connect()
        logger.info(f"初始化知识图谱数据仓库: {url}")
    
    def _connect(self):
        """建立Neo4j连接"""
        try:
            self._driver = GraphDatabase.driver(
                self._url, 
                auth=(self._user, self._password)
            )
            self._driver.verify_connectivity()
            logger.info("Neo4j连接成功")
        except AuthError as e:
            logger.error(f"Neo4j认证失败: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j服务不可用: {e}")
            raise
        except Exception as e:
            logger.error(f"Neo4j连接异常: {e}")
            raise
    
    def close(self):
        """关闭连接"""
        if self._driver:
            self._driver.close()
    
    def _get_session(self):
        return self._driver.session(database=self._database)
    
    def search_nodes(self, keyword: str, limit: int = 3) -> List[Dict]:
        """搜索包含关键词的节点"""
        with self._get_session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.name CONTAINS $keyword
                OPTIONAL MATCH (n)-[r]->(child)
                WITH n, type(r) as rel_type, collect(child.name)[0..3] as children
                RETURN DISTINCT n.name as name, labels(n)[0] as type, 
                       collect(DISTINCT {rel: rel_type, children: children}) as relations
                LIMIT $limit
            """, keyword=keyword, limit=limit)
            return [dict(record) for record in result]
    
    def get_learning_path_by_topic(self, topic: str, limit: int = 5) -> List[Dict]:
        """根据主题获取学习路径"""
        with self._get_session() as session:
            result = session.run("""
                MATCH path = (c:Course)-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_SECTION]->(s:Section)
                WHERE s.name CONTAINS $topic OR ch.name CONTAINS $topic
                RETURN c.name as course, ch.name as chapter, s.name as section
                LIMIT $limit
            """, topic=topic, limit=limit)
            return [dict(record) for record in result]
    
    def get_course_outline(self, course_type: str) -> Dict:
        """获取课程大纲（包含详细知识点层级）"""
        with self._get_session() as session:
            result = session.run("""
                MATCH (c:Course {id: $course_id})-[r:HAS_CHAPTER]->(ch:Chapter)
                OPTIONAL MATCH (ch)-[:HAS_SECTION]->(s:Section)
                OPTIONAL MATCH (s)-[:HAS_KNOWLEDGE_POINT]->(kp)
                OPTIONAL MATCH (kp)-[:HAS_SUB_POINT]->(sub)
                WITH c, ch, r.order as ch_order, s, kp, sub
                ORDER BY ch_order, s.name, kp.name, sub.name
                RETURN c.name as course, 
                       ch.name as chapter, 
                       ch_order,
                       s.name as section_name,
                       s.id as section_id,
                       kp.id as kp_id,
                       kp.name as kp_name,
                       labels(kp)[0] as kp_type,
                       sub.id as sub_id,
                       sub.name as sub_name,
                       labels(sub)[0] as sub_type
            """, course_id=f"course_{course_type}")
            
            chapters_dict = {}
            course_name = ""
            
            for record in result:
                if not course_name:
                    course_name = record["course"]
                
                ch_order = record["ch_order"]
                ch_name = record["chapter"]
                
                if ch_order not in chapters_dict:
                    chapters_dict[ch_order] = {
                        "order": ch_order,
                        "chapter": ch_name,
                        "sections": {}
                    }
                
                section_name = record["section_name"]
                section_id = record["section_id"]
                
                if section_name and section_id:
                    if section_id not in chapters_dict[ch_order]["sections"]:
                        chapters_dict[ch_order]["sections"][section_id] = {
                            "name": section_name,
                            "id": section_id,
                            "knowledge_points": {}
                        }
                    
                    kp_id = record["kp_id"]
                    kp_name = record["kp_name"]
                    kp_type = record["kp_type"]
                    
                    if kp_id and kp_name:
                        if kp_id not in chapters_dict[ch_order]["sections"][section_id]["knowledge_points"]:
                            chapters_dict[ch_order]["sections"][section_id]["knowledge_points"][kp_id] = {
                                "id": kp_id,
                                "name": kp_name,
                                "type": kp_type,
                                "sub_points": []
                            }
                        
                        sub_id = record["sub_id"]
                        sub_name = record["sub_name"]
                        sub_type = record["sub_type"]
                        
                        if sub_id and sub_name:
                            chapters_dict[ch_order]["sections"][section_id]["knowledge_points"][kp_id]["sub_points"].append({
                                "id": sub_id,
                                "name": sub_name,
                                "type": sub_type
                            })
            
            chapters = []
            for order in sorted(chapters_dict.keys()):
                ch_data = chapters_dict[order]
                sections = []
                for sec_id in ch_data["sections"]:
                    sec_data = ch_data["sections"][sec_id]
                    knowledge_points = []
                    for kp_id in sec_data["knowledge_points"]:
                        kp_data = sec_data["knowledge_points"][kp_id]
                        knowledge_points.append({
                            "id": kp_data["id"],
                            "name": kp_data["name"],
                            "type": kp_data["type"],
                            "sub_points": kp_data["sub_points"]
                        })
                    sections.append({
                        "id": sec_data["id"],
                        "name": sec_data["name"],
                        "knowledge_points": knowledge_points
                    })
                chapters.append({
                    "order": ch_data["order"],
                    "chapter": ch_data["chapter"],
                    "sections": sections
                })
            
            return {"course": course_name, "chapters": chapters}
    
    def get_chapters_by_course(self, course_id: str) -> List[str]:
        """获取课程的章节列表"""
        with self._get_session() as session:
            result = session.run("""
                MATCH (c:Course {id: $course_id})-[r:HAS_CHAPTER]->(ch:Chapter)
                RETURN ch.name as name, r.order as order
                ORDER BY toInteger(r.order)
            """, course_id=course_id)
            return [r['name'] for r in result]
    
    def get_all_topics(self, limit: int = 100) -> List[str]:
        """获取所有主题"""
        with self._get_session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.name IS NOT NULL AND n.name <> ''
                RETURN DISTINCT n.name as name
                ORDER BY name
                LIMIT $limit
            """, limit=limit)
            return [record['name'] for record in result]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self._get_session() as session:
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()['count']
            
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()['count']
            
            return {"nodes": node_count, "relations": rel_count}
    
    def get_all_knowledge_points(self, course_type: str) -> List[Dict]:
        """
        获取课程的所有知识点（细分到最小知识点级别）
        
        返回结构：
        [
            {
                "knowledge_point_id": "course_basic_ch_0_sec_0_kp_0",
                "knowledge_point_name": "Python3简介",
                "course_type": "basic",
                "chapter_name": "Python3介绍",
                "section_name": "Python3简介"
            },
            ...
        ]
        """
        with self._get_session() as session:
            result = session.run("""
                MATCH (c:Course {id: $course_id})-[:HAS_CHAPTER]->(ch:Chapter)
                OPTIONAL MATCH (ch)-[:HAS_SECTION]->(s:Section)
                OPTIONAL MATCH (s)-[:HAS_KNOWLEDGE_POINT]->(kp)
                WITH c, ch, s, kp
                ORDER BY ch.name, s.name, kp.name
                RETURN c.name as course_name, 
                       ch.name as chapter_name,
                       s.name as section_name,
                       kp.id as knowledge_point_id,
                       kp.name as knowledge_point_name,
                       labels(kp)[0] as knowledge_point_type
            """, course_id=f"course_{course_type}")
            
            knowledge_points = []
            for record in result:
                if record["knowledge_point_id"]:
                    knowledge_points.append({
                        "knowledge_point_id": record["knowledge_point_id"],
                        "knowledge_point_name": record["knowledge_point_name"],
                        "knowledge_point_type": record["knowledge_point_type"],
                        "course_type": course_type,
                        "chapter_name": record["chapter_name"],
                        "section_name": record["section_name"]
                    })
            
            return knowledge_points
    
    def get_graph_data(self, course_type: str = None, depth: int = 4) -> Dict:
        """
        获取知识图谱可视化数据
        
        Args:
            course_type: 课程类型 (basic/advanced)，为None时获取全部
            depth: 层级深度 (1-4)
                   1: 仅课程
                   2: 课程+章节
                   3: 课程+章节+小节
                   4: 全部层级（包含知识点）
        
        Returns:
            {
                "nodes": [{"id": "...", "name": "...", "type": "...", "parentId": "..."}],
                "edges": [{"source": "...", "target": "...", "type": "..."}]
            }
        """
        nodes = []
        edges = []
        node_ids = set()
        
        with self._get_session() as session:
            if course_type:
                course_filter = f"AND c.id = 'course_{course_type}'"
            else:
                course_filter = ""
            
            result = session.run(f"""
                MATCH (c:Course)
                WHERE 1=1 {course_filter}
                OPTIONAL MATCH (c)-[r1:HAS_CHAPTER]->(ch:Chapter)
                OPTIONAL MATCH (ch)-[r2:HAS_SECTION]->(s:Section)
                OPTIONAL MATCH (s)-[r3:HAS_KNOWLEDGE_POINT]->(kp)
                OPTIONAL MATCH (kp)-[r4:HAS_SUB_POINT]->(sub)
                RETURN c.id as course_id, c.name as course_name,
                       ch.id as chapter_id, ch.name as chapter_name, r1.order as ch_order,
                       s.id as section_id, s.name as section_name,
                       kp.id as kp_id, kp.name as kp_name, labels(kp)[0] as kp_type,
                       sub.id as sub_id, sub.name as sub_name, labels(sub)[0] as sub_type
                ORDER BY ch_order, chapter_name, section_name, kp_name, sub_name
            """)
            
            for record in result:
                course_id = record["course_id"]
                course_name = record["course_name"]
                
                if course_id and course_id not in node_ids:
                    nodes.append({
                        "id": course_id,
                        "name": course_name,
                        "type": "Course",
                        "parentId": None
                    })
                    node_ids.add(course_id)
                
                if depth >= 2:
                    chapter_id = record["chapter_id"]
                    chapter_name = record["chapter_name"]
                    
                    if chapter_id and chapter_id not in node_ids:
                        nodes.append({
                            "id": chapter_id,
                            "name": chapter_name,
                            "type": "Chapter",
                            "parentId": course_id
                        })
                        node_ids.add(chapter_id)
                        edges.append({
                            "source": course_id,
                            "target": chapter_id,
                            "type": "HAS_CHAPTER"
                        })
                
                if depth >= 3:
                    section_id = record["section_id"]
                    section_name = record["section_name"]
                    chapter_id = record["chapter_id"]
                    
                    if section_id and section_id not in node_ids and chapter_id:
                        nodes.append({
                            "id": section_id,
                            "name": section_name,
                            "type": "Section",
                            "parentId": chapter_id
                        })
                        node_ids.add(section_id)
                        edges.append({
                            "source": chapter_id,
                            "target": section_id,
                            "type": "HAS_SECTION"
                        })
                
                if depth >= 4:
                    kp_id = record["kp_id"]
                    kp_name = record["kp_name"]
                    kp_type = record["kp_type"]
                    section_id = record["section_id"]
                    
                    if kp_id and kp_id not in node_ids and section_id:
                        nodes.append({
                            "id": kp_id,
                            "name": kp_name,
                            "type": kp_type or "KnowledgePoint",
                            "parentId": section_id
                        })
                        node_ids.add(kp_id)
                        edges.append({
                            "source": section_id,
                            "target": kp_id,
                            "type": "HAS_KNOWLEDGE_POINT"
                        })
                    
                    sub_id = record["sub_id"]
                    sub_name = record["sub_name"]
                    sub_type = record["sub_type"]
                    
                    if sub_id and sub_id not in node_ids and kp_id:
                        nodes.append({
                            "id": sub_id,
                            "name": sub_name,
                            "type": sub_type or "SubPoint",
                            "parentId": kp_id
                        })
                        node_ids.add(sub_id)
                        edges.append({
                            "source": kp_id,
                            "target": sub_id,
                            "type": "HAS_SUB_POINT"
                        })
        
        unique_edges = []
        seen_edges = set()
        for edge in edges:
            edge_key = f"{edge['source']}-{edge['target']}-{edge['type']}"
            if edge_key not in seen_edges:
                unique_edges.append(edge)
                seen_edges.add(edge_key)
        
        return {"nodes": nodes, "edges": unique_edges}
