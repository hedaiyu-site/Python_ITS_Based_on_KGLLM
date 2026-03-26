"""
知识图谱业务服务

提供知识图谱查询、学习路径推荐等业务逻辑
"""

from typing import List, Dict
import logging

from app.repositories.neo4j.kg_repository import KnowledgeGraphRepository

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """知识图谱业务服务"""
    
    def __init__(self, kg_repository: KnowledgeGraphRepository):
        self._kg_repo = kg_repository
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self._kg_repo.get_statistics()
    
    def get_all_topics(self) -> List[str]:
        """获取所有主题"""
        return self._kg_repo.get_all_topics()
    
    def get_course_outline(self, course_type: str) -> Dict:
        """获取课程大纲"""
        return self._kg_repo.get_course_outline(course_type)
    
    def get_learning_path(self, topic: str) -> List[Dict]:
        """获取学习路径"""
        return self._kg_repo.get_learning_path_by_topic(topic)
    
    def search_context(self, keyword: str) -> str:
        """搜索知识上下文"""
        if not keyword:
            return ""
        
        nodes = self._kg_repo.search_nodes(keyword)
        
        context_parts = []
        for node in nodes:
            name = node['name']
            node_type = node['type']
            info = f"【{node_type}】{name}"
            
            for rel_info in node['relations'][:2]:
                if rel_info['children']:
                    info += f"\n  - {rel_info['rel']}: {', '.join(rel_info['children'])}"
            context_parts.append(info)
        
        return "\n\n".join(context_parts)
    
    def get_learning_path_by_level(self, level: str = "beginner") -> str:
        """根据用户水平获取学习路径"""
        basic_chapters = self._kg_repo.get_chapters_by_course("course_basic")
        advanced_chapters = self._kg_repo.get_chapters_by_course("course_advanced")
        
        if level == "beginner":
            path = "【Python初学者学习路径】\n\n"
            path += "建议按以下顺序学习基础课程：\n\n"
            path += "📚 Python基础编程教程\n"
            for i, ch in enumerate(basic_chapters, 1):
                path += f"   {i}. {ch}\n"
            path += "\n💡 学习建议：\n"
            path += "   - 每学完一章做练习巩固\n"
            path += "   - 重点掌握数据类型和流程控制\n"
            path += "   - 理解函数和面向对象概念\n"
            
        elif level == "intermediate":
            path = "【Python进阶学习路径】\n\n"
            path += "假设你已掌握Python基础，建议学习：\n\n"
            path += "📚 Python高级教程\n"
            for i, ch in enumerate(advanced_chapters, 1):
                path += f"   {i}. {ch}\n"
            path += "\n💡 学习建议：\n"
            path += "   - 深入学习标准库和并发编程\n"
            path += "   - 掌握网络编程和数据处理\n"
            path += "   - 尝试实际项目开发\n"
            
        else:
            path = "【Python完整学习路径】\n\n"
            path += "一、基础阶段\n"
            for i, ch in enumerate(basic_chapters, 1):
                path += f"   {i}. {ch}\n"
            path += "\n二、进阶阶段\n"
            for i, ch in enumerate(advanced_chapters, 1):
                path += f"   {i}. {ch}\n"
        
        return path
    
    def get_graph_data(self, course_type: str = None, depth: int = 4) -> Dict:
        """
        获取知识图谱可视化数据
        
        Args:
            course_type: 课程类型 (basic/advanced)，为None时获取全部
            depth: 层级深度 (1-4)
        
        Returns:
            包含nodes和edges的字典
        """
        if depth < 1:
            depth = 1
        elif depth > 4:
            depth = 4
        
        return self._kg_repo.get_graph_data(course_type, depth)
