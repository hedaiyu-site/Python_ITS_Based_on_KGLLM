"""
对话模块测试
"""

import pytest
import json


class TestChatStream:
    """流式对话测试"""
    
    def test_chat_stream_success(self, client, auth_headers):
        """测试流式对话成功"""
        response = client.post(
            "/api/chat",
            json={
                "message": "什么是列表？",
                "context": ""
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
    
    def test_chat_stream_with_context(self, client, auth_headers):
        """测试带上下文的流式对话"""
        response = client.post(
            "/api/chat",
            json={
                "message": "请详细解释",
                "context": "Python是一种编程语言"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_chat_stream_with_session(self, client, auth_headers):
        """测试带会话ID的流式对话"""
        response = client.post(
            "/api/chat",
            json={
                "message": "什么是函数？",
                "context": "",
                "session_id": "test-session-123"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_chat_missing_message(self, client, auth_headers):
        """测试缺少消息字段"""
        response = client.post(
            "/api/chat",
            json={
                "context": "some context"
            },
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_chat_unauthorized(self, client):
        """测试未授权访问"""
        response = client.post(
            "/api/chat",
            json={
                "message": "测试消息",
                "context": ""
            }
        )
        assert response.status_code == 401


class TestChatKeywords:
    """关键词提取测试"""
    
    def test_chat_python_keyword(self, client, auth_headers):
        """测试Python关键词识别"""
        response = client.post(
            "/api/chat",
            json={
                "message": "函数和列表有什么区别？",
                "context": ""
            },
            headers=auth_headers
        )
        assert response.status_code == 200
    
    def test_chat_chinese_keyword(self, client, auth_headers):
        """测试中文关键词识别"""
        response = client.post(
            "/api/chat",
            json={
                "message": "什么是类？",
                "context": ""
            },
            headers=auth_headers
        )
        assert response.status_code == 200
