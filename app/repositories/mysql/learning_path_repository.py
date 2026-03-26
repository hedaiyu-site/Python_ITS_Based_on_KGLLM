"""
学习路径数据仓库

提供学习路径相关的数据库操作
"""

import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class LearningPathRepository:
    """
    学习路径数据仓库
    
    负责学习路径和知识点进度的CRUD操作
    """
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self._config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": "utf8mb4"
        }
        # logger.info(f"初始化学习路径数据仓库: {host}:{port}/{database}")
    
    def _get_connection(self):
        return pymysql.connect(**self._config)
    
    def create_user_profile(self, user_id: int, learning_path: str) -> int:
        """创建用户学习档案"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO user_learning_profiles (user_id, learning_path) VALUES (%s, %s)",
                    (user_id, learning_path)
                )
                conn.commit()
                return cursor.lastrowid
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户学习档案"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM user_learning_profiles WHERE user_id = %s",
                    (user_id,)
                )
                return cursor.fetchone()
    
    def update_knowledge_progress(
        self, 
        user_id: int, 
        knowledge_point_id: str,
        knowledge_point_name: str,
        course_type: str = None,
        chapter_name: str = None,
        section_name: str = None,
        status: str = "learning",
        mastery_level: int = 0,
        quiz_score: float = 0
    ):
        """更新或创建知识点进度"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO knowledge_progress 
                    (user_id, knowledge_point_id, knowledge_point_name, course_type, chapter_name, section_name, status, mastery_level, quiz_score, last_study_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                    knowledge_point_name = VALUES(knowledge_point_name),
                    course_type = VALUES(course_type),
                    chapter_name = VALUES(chapter_name),
                    section_name = VALUES(section_name),
                    status = VALUES(status),
                    mastery_level = VALUES(mastery_level),
                    quiz_score = VALUES(quiz_score),
                    last_study_time = NOW(),
                    updated_at = NOW()
                """
                cursor.execute(sql, (
                    user_id, knowledge_point_id, knowledge_point_name, 
                    course_type, chapter_name, section_name, status, mastery_level, quiz_score
                ))
                conn.commit()
    
    def increment_quiz_stats(self, user_id: int, knowledge_point_id: str, is_correct: bool):
        """增加测验统计"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE knowledge_progress 
                    SET quiz_count = quiz_count + 1,
                        correct_count = correct_count + %s,
                        last_study_time = NOW()
                    WHERE user_id = %s AND knowledge_point_id = %s
                """
                cursor.execute(sql, (1 if is_correct else 0, user_id, knowledge_point_id))
                conn.commit()
    
    def get_knowledge_progress(self, user_id: int, knowledge_point_id: str) -> Optional[Dict[str, Any]]:
        """获取知识点进度"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM knowledge_progress WHERE user_id = %s AND knowledge_point_id = %s",
                    (user_id, knowledge_point_id)
                )
                return cursor.fetchone()
    
    def get_all_knowledge_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户所有知识点进度"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM knowledge_progress WHERE user_id = %s ORDER BY updated_at DESC",
                    (user_id,)
                )
                return cursor.fetchall()
    
    def get_learning_path_config(self, path_type: str) -> Optional[Dict[str, Any]]:
        """获取学习路径配置"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM learning_path_configs WHERE path_type = %s",
                    (path_type,)
                )
                return cursor.fetchone()
    
    def get_progress_statistics(self, user_id: int) -> Dict[str, Any]:
        """获取学习进度统计"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_knowledge_points,
                        SUM(CASE WHEN status = 'mastered' THEN 1 ELSE 0 END) as mastered_count,
                        SUM(CASE WHEN status = 'learning' THEN 1 ELSE 0 END) as learning_count,
                        AVG(mastery_level) as avg_mastery_level
                    FROM knowledge_progress
                    WHERE user_id = %s
                """, (user_id,))
                return cursor.fetchone()
    
    def get_structured_progress(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取结构化的学习进度数据
        
        返回按课程、章节、小节组织的知识点进度
        """
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        course_type,
                        chapter_name,
                        section_name,
                        knowledge_point_id,
                        knowledge_point_name,
                        status,
                        mastery_level,
                        quiz_score,
                        quiz_count,
                        correct_count
                    FROM knowledge_progress
                    WHERE user_id = %s
                    ORDER BY course_type, chapter_name, section_name, knowledge_point_name
                """, (user_id,))
                return cursor.fetchall()
