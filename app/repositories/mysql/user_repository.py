"""
用户数据仓库

提供用户相关的数据库操作
"""

import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """
    用户数据仓库
    
    负责用户数据的CRUD操作
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
        # logger.info(f"初始化用户数据仓库: {host}:{port}/{database}")
    
    def _get_connection(self):
        return pymysql.connect(**self._config)
    
    def create(self, username: str, password: str, email: Optional[str] = None, learning_path: str = "basic") -> int:
        """创建用户，返回用户ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password, email, learning_path) VALUES (%s, %s, %s, %s)",
                    (username, password, email, learning_path)
                )
                conn.commit()
                return cursor.lastrowid
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名查找用户"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT id, username, password, email, learning_path, created_at, is_active FROM users WHERE username = %s",
                    (username,)
                )
                return cursor.fetchone()
    
    def find_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查找用户"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT id, username, email, created_at, is_active FROM users WHERE id = %s",
                    (user_id,)
                )
                return cursor.fetchone()
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱查找用户"""
        with self._get_connection() as conn:
            with conn.cursor(DictCursor) as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,)
                )
                return cursor.fetchone()
    
    def exists_by_username(self, username: str) -> bool:
        """检查用户名是否存在"""
        return self.find_by_username(username) is not None
    
    def exists_by_email(self, email: str) -> bool:
        """检查邮箱是否存在"""
        return self.find_by_email(email) is not None
