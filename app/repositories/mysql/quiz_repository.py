"""
测验题目数据仓库

提供测验题目相关的数据库操作
"""

import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class QuizRepository:
    """
    测验题目数据仓库
    
    负责测验题目的CRUD操作
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
        # logger.info(f"初始化测验题目数据仓库: {host}:{port}/{database}")
    
    def _get_connection(self):
        return pymysql.connect(**self._config)
    
    def create_question(
        self,
        knowledge_point_id: str,
        knowledge_point_name: str,
        question: str,
        option_a: str,
        option_b: str,
        option_c: str,
        option_d: str,
        correct_answer: str,
        explanation: str = None,
        difficulty: str = "medium"
    ) -> int:
        """创建测验题目"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO quiz_questions 
                    (knowledge_point_id, knowledge_point_name, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    knowledge_point_id, knowledge_point_name, question,
                    option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty
                ))
                conn.commit()
                return cursor.lastrowid
    
    def get_questions_by_knowledge_point(self, knowledge_point_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取知识点的测验题目（支持模糊匹配）"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM quiz_questions WHERE knowledge_point_id LIKE %s ORDER BY RAND() LIMIT %s",
                    (f"{knowledge_point_id}%", limit)
                )
                return cursor.fetchall()
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取题目"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM quiz_questions WHERE id = %s",
                    (question_id,)
                )
                return cursor.fetchone()
    
    def count_questions_by_knowledge_point(self, knowledge_point_id: str) -> int:
        """统计知识点的题目数量（支持模糊匹配）"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM quiz_questions WHERE knowledge_point_id LIKE %s",
                    (f"{knowledge_point_id}%",)
                )
                result = cursor.fetchone()
                return result[0] if result else 0
    
    def save_quiz_record(
        self,
        user_id: int,
        knowledge_point_id: str,
        question_id: int,
        user_answer: str,
        is_correct: bool
    ):
        """保存测验记录"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO user_quiz_records 
                    (user_id, knowledge_point_id, question_id, user_answer, is_correct)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (user_id, knowledge_point_id, question_id, user_answer, is_correct))
                conn.commit()
    
    def get_user_quiz_history(self, user_id: int, knowledge_point_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户测验历史"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                sql = """
                    SELECT r.*, q.question, q.correct_answer, q.explanation
                    FROM user_quiz_records r
                    JOIN quiz_questions q ON r.question_id = q.id
                    WHERE r.user_id = %s AND r.knowledge_point_id = %s
                    ORDER BY r.quiz_time DESC
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, knowledge_point_id, limit))
                return cursor.fetchall()
    
    def get_all_knowledge_points_with_questions(self) -> List[Dict[str, Any]]:
        """获取所有有题目的知识点（按基础教程→高级教程顺序排列）"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT knowledge_point_id, knowledge_point_name, COUNT(*) as question_count
                    FROM quiz_questions
                    GROUP BY knowledge_point_id, knowledge_point_name
                    ORDER BY 
                        CASE 
                            WHEN knowledge_point_id LIKE 'course_basic%' THEN 0
                            WHEN knowledge_point_id LIKE 'course_advanced%' THEN 1
                            ELSE 2
                        END,
                        knowledge_point_id
                """)
                return cursor.fetchall()
