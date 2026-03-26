"""
聊天历史模块测试
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient


class TestChatHistory:
    """聊天历史测试"""
    
    def test_get_sessions_success(self, client, auth_headers):
        """测试获取会话列表成功"""
        response = client.get("/api/history/sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sessions" in data
        assert isinstance(data["sessions"], list)
    
    def test_get_sessions_unauthorized(self, client):
        """测试未授权访问会话列表"""
        response = client.get("/api/history/sessions")
        assert response.status_code == 401
    
    def test_get_recent_history_success(self, client, auth_headers):
        """测试获取最近聊天记录成功"""
        response = client.get("/api/history/recent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    def test_get_recent_history_with_limit(self, client, auth_headers):
        """测试带限制的最近聊天记录"""
        response = client.get("/api/history/recent?limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_session_history_not_found(self, client, auth_headers):
        """测试获取不存在的会话历史"""
        response = client.get(
            "/api/history/session/non-existent-session-id", 
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["messages"] == []
    
    def test_delete_session_success(self, client, auth_headers):
        """测试删除会话成功"""
        response = client.delete(
            "/api/history/session/test-session-id",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_clear_history_success(self, client, auth_headers):
        """测试清空聊天记录"""
        response = client.delete("/api/history/clear", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted_count" in data


class TestChatWithHistory:
    """带历史记录的对话测试"""
    
    def test_chat_creates_session(self, client, auth_headers):
        """测试对话创建会话"""
        response = client.post(
            "/api/chat",
            json={
                "message": "什么是函数？",
                "context": ""
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "response" in data
        assert "session_id" in data
    
    def test_chat_continues_session(self, client, auth_headers):
        """测试继续会话对话"""
        first_response = client.post(
            "/api/chat",
            json={
                "message": "什么是列表？",
                "context": ""
            },
            headers=auth_headers
        )
        assert first_response.status_code == 200
        first_data = first_response.json()
        session_id = first_data.get("session_id")
        
        if session_id:
            second_response = client.post(
                "/api/chat",
                json={
                    "message": "能详细解释一下吗？",
                    "context": "",
                    "session_id": session_id
                },
                headers=auth_headers
            )
            assert second_response.status_code == 200
            second_data = second_response.json()
            assert second_data["session_id"] == session_id
    
    def test_chat_stream_creates_session(self, client, auth_headers):
        """测试流式对话创建会话"""
        response = client.post(
            "/api/chat",
            json={
                "message": "什么是字典？",
                "context": ""
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
