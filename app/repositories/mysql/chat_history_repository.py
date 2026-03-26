"""
聊天记录数据仓库

提供聊天记录的数据库操作
"""

import pymysql
from pymysql.cursors import DictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    """
    聊天记录数据仓库
    
    负责聊天记录的CRUD操作
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
        # logger.info(f"初始化聊天记录数据仓库: {host}:{port}/{database}")
    
    def _get_connection(self):
        return pymysql.connect(**self._config)
    
    def create_table(self):
        """创建聊天记录表"""
        create_sql = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_id VARCHAR(64) NOT NULL,
            role ENUM('user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            INDEX idx_session_id (session_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_sql)
                conn.commit()
        # logger.info("聊天记录表创建成功")
    
    def save_message(self, user_id: int, session_id: str, role: str, content: str) -> int:
        """保存聊天消息，返回消息ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO chat_history (user_id, session_id, role, content) 
                       VALUES (%s, %s, %s, %s)""",
                    (user_id, session_id, role, content)
                )
                conn.commit()
                return cursor.lastrowid
    
    def get_session_history(self, user_id: int, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取指定会话的历史记录"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    """SELECT id, role, content, created_at 
                       FROM chat_history 
                       WHERE user_id = %s AND session_id = %s 
                       ORDER BY created_at ASC 
                       LIMIT %s""",
                    (user_id, session_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_user_sessions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的所有会话列表"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    """SELECT session_id, MIN(created_at) as started_at, 
                              MAX(created_at) as last_message_at,
                              COUNT(*) as message_count
                       FROM chat_history 
                       WHERE user_id = %s 
                       GROUP BY session_id 
                       ORDER BY last_message_at DESC 
                       LIMIT %s""",
                    (user_id, limit)
                )
                return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户最近的聊天记录"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    """SELECT id, session_id, role, content, created_at 
                       FROM chat_history 
                       WHERE user_id = %s 
                       ORDER BY created_at DESC 
                       LIMIT %s""",
                    (user_id, limit)
                )
                results = [dict(row) for row in cursor.fetchall()]
                return list(reversed(results))
    
    def delete_session(self, user_id: int, session_id: str) -> int:
        """删除指定会话的所有记录，返回删除的记录数"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM chat_history WHERE user_id = %s AND session_id = %s",
                    (user_id, session_id)
                )
                conn.commit()
                return cursor.rowcount
    
    def clear_user_history(self, user_id: int) -> int:
        """清空用户所有聊天记录，返回删除的记录数"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM chat_history WHERE user_id = %s",
                    (user_id,)
                )
                conn.commit()
                return cursor.rowcount
    
    def get_session_first_message(self, user_id: int, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话的第一条消息（用于显示会话标题）"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    """SELECT content FROM chat_history 
                       WHERE user_id = %s AND session_id = %s AND role = 'user'
                       ORDER BY created_at ASC 
                       LIMIT 1""",
                    (user_id, session_id)
                )
                return cursor.fetchone()
