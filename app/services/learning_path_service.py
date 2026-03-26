"""
学习路径业务服务

提供学习路径管理、知识点进度跟踪等业务逻辑
"""

from typing import List, Dict, Any, Optional
import logging
import json

from app.repositories.mysql.learning_path_repository import LearningPathRepository
from app.repositories.neo4j.kg_repository import KnowledgeGraphRepository

logger = logging.getLogger(__name__)


class LearningPathService:
    """学习路径业务服务"""
    
    def __init__(
        self, 
        learning_path_repository: LearningPathRepository,
        kg_repository: KnowledgeGraphRepository
    ):
        self._learning_path_repo = learning_path_repository
        self._kg_repo = kg_repository
    
    def initialize_user_learning_path(self, user_id: int, learning_path: str) -> Dict[str, Any]:
        """
        初始化用户学习路径
        
        根据选择的学习路径，从知识图谱中提取所有最小知识点并初始化进度
        """
        profile = self._learning_path_repo.create_user_profile(user_id, learning_path)
        
        path_config = self._learning_path_repo.get_learning_path_config(learning_path)
        if not path_config:
            raise ValueError(f"无效的学习路径: {learning_path}")
        
        course_ids = json.loads(path_config['course_ids'])
        
        total_knowledge_points = 0
        for course_id in course_ids:
            course_type = "basic" if "basic" in course_id else "advanced"
            
            knowledge_points = self._kg_repo.get_all_knowledge_points(course_type)
            
            for kp in knowledge_points:
                self._learning_path_repo.update_knowledge_progress(
                    user_id=user_id,
                    knowledge_point_id=kp['knowledge_point_id'],
                    knowledge_point_name=kp['knowledge_point_name'],
                    course_type=kp['course_type'],
                    chapter_name=kp['chapter_name'],
                    section_name=kp['section_name'],
                    status="not_started",
                    mastery_level=0
                )
                total_knowledge_points += 1
        
        logger.info(f"初始化用户学习路径: user_id={user_id}, path={learning_path}, total_kp={total_knowledge_points}")
        
        return {
            "user_id": user_id,
            "learning_path": learning_path,
            "total_knowledge_points": total_knowledge_points
        }
    
    def update_knowledge_progress(
        self,
        user_id: int,
        knowledge_point_id: str,
        knowledge_point_name: str,
        quiz_score: float = 0,
        correct_count: int = 0,
        total_count: int = 0
    ):
        """
        根据测验结果更新知识点掌握程度
        
        计算逻辑：
        - 掌握程度 = (答对题数 / 总题数) * 100
        - 如果掌握程度 >= 80，状态为 mastered
        - 如果掌握程度 >= 50，状态为 learning
        - 如果掌握程度 < 50，状态为 reviewing
        """
        mastery_level = int((correct_count / total_count * 100) if total_count > 0 else 0)
        
        if mastery_level >= 80:
            status = "mastered"
        elif mastery_level >= 50:
            status = "learning"
        else:
            status = "reviewing"
        
        self._learning_path_repo.update_knowledge_progress(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            knowledge_point_name=knowledge_point_name,
            status=status,
            mastery_level=mastery_level,
            quiz_score=quiz_score
        )
        
        logger.info(f"更新知识点进度: user_id={user_id}, kp={knowledge_point_name}, mastery={mastery_level}%")
    
    def get_user_learning_progress(self, user_id: int) -> Dict[str, Any]:
        """获取用户学习进度"""
        profile = self._learning_path_repo.get_user_profile(user_id)
        if not profile:
            return {
                "success": False,
                "message": "用户学习档案不存在"
            }
        
        all_progress = self._learning_path_repo.get_all_knowledge_progress(user_id)
        statistics = self._learning_path_repo.get_progress_statistics(user_id)
        
        mastered_count = statistics.get('mastered_count', 0) or 0
        total_count = statistics.get('total_knowledge_points', 0) or 0
        progress_percentage = (mastered_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "success": True,
            "learning_path": profile['learning_path'],
            "total_knowledge_points": total_count,
            "mastered_count": mastered_count,
            "learning_count": statistics.get('learning_count', 0) or 0,
            "progress_percentage": round(progress_percentage, 2),
            "avg_mastery_level": round(statistics.get('avg_mastery_level', 0) or 0, 2),
            "knowledge_points": all_progress
        }
    
    def get_knowledge_point_detail(self, user_id: int, knowledge_point_id: str) -> Optional[Dict[str, Any]]:
        """获取知识点详细进度"""
        return self._learning_path_repo.get_knowledge_progress(user_id, knowledge_point_id)
