"""
聊天记录业务服务

提供聊天记录的业务逻辑
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from app.repositories.mysql.chat_history_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)


class ChatHistoryService:
    """聊天记录业务服务"""
    
    def __init__(self, chat_history_repository: ChatHistoryRepository):
        self._chat_history_repo = chat_history_repository
    
    def create_session(self) -> str:
        """创建新的会话ID"""
        return str(uuid.uuid4())
    
    def save_user_message(self, user_id: int, session_id: str, content: str) -> int:
        """保存用户消息"""
        return self._chat_history_repo.save_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=content
        )
    
    def save_assistant_message(self, user_id: int, session_id: str, content: str) -> int:
        """保存助手消息"""
        return self._chat_history_repo.save_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=content
        )
    
    def get_session_history(self, user_id: int, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取会话历史记录"""
        messages = self._chat_history_repo.get_session_history(user_id, session_id, limit)
        return [
            {
                "id": msg["id"],
                "role": msg["role"],
                "content": msg["content"],
                "created_at": msg["created_at"].isoformat() if isinstance(msg["created_at"], datetime) else msg["created_at"]
            }
            for msg in messages
        ]
    
    def get_user_sessions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        sessions = self._chat_history_repo.get_user_sessions(user_id, limit)
        result = []
        for session in sessions:
            first_msg = self._chat_history_repo.get_session_first_message(
                user_id, session["session_id"]
            )
            title = self._generate_session_title(first_msg["content"] if first_msg else "新对话")
            result.append({
                "session_id": session["session_id"],
                "title": title,
                "started_at": session["started_at"].isoformat() if isinstance(session["started_at"], datetime) else session["started_at"],
                "last_message_at": session["last_message_at"].isoformat() if isinstance(session["last_message_at"], datetime) else session["last_message_at"],
                "message_count": session["message_count"]
            })
        return result
    
    def get_recent_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户最近的聊天记录"""
        messages = self._chat_history_repo.get_recent_history(user_id, limit)
        return [
            {
                "id": msg["id"],
                "session_id": msg["session_id"],
                "role": msg["role"],
                "content": msg["content"],
                "created_at": msg["created_at"].isoformat() if isinstance(msg["created_at"], datetime) else msg["created_at"]
            }
            for msg in messages
        ]
    
    def delete_session(self, user_id: int, session_id: str) -> bool:
        """删除会话"""
        count = self._chat_history_repo.delete_session(user_id, session_id)
        return count > 0
    
    def clear_user_history(self, user_id: int) -> int:
        """清空用户所有聊天记录"""
        return self._chat_history_repo.clear_user_history(user_id)
    
    def get_context_for_chat(self, user_id: int, session_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """获取用于对话的上下文消息列表"""
        messages = self._chat_history_repo.get_session_history(user_id, session_id, max_messages)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
    def _generate_session_title(self, first_message: str, max_length: int = 30) -> str:
        """根据第一条消息生成会话标题"""
        if not first_message:
            return "新对话"
        
        title = first_message.strip().replace("\n", " ")
        if len(title) > max_length:
            return title[:max_length] + "..."
        return title
