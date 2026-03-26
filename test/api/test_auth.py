"""
用户认证模块测试
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock


class TestAuthRegister:
    """用户注册测试"""
    
    def test_register_success(self, client):
        """测试注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "password123",
                "email": "newuser@example.com"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "注册成功"
        assert data["user"]["username"] == "newuser"
    
    def test_register_username_too_short(self, client):
        """测试用户名过短"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "ab",
                "password": "password123"
            }
        )
        assert response.status_code == 422
    
    def test_register_password_too_short(self, client):
        """测试密码过短"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "12345"
            }
        )
        assert response.status_code == 422
    
    def test_register_invalid_email(self, client):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "password": "password123",
                "email": "invalid-email"
            }
        )
        assert response.status_code == 422


class TestAuthLogin:
    """用户登录测试"""
    
    def test_login_success(self, client):
        """测试登录成功"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"
    
    def test_login_missing_fields(self, client):
        """测试缺少字段"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser"
            }
        )
        assert response.status_code == 422


class TestAuthMe:
    """获取当前用户测试"""
    
    def test_get_current_user_success(self, client, auth_headers):
        """测试获取当前用户成功"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_get_current_user_no_token(self, client):
        """测试无token返回401"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """测试无效token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code in [401, 422]
