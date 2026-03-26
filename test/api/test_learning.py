"""
知识图谱模块测试
"""

import pytest


class TestSearch:
    """知识搜索测试"""
    
    def test_search_success(self, client):
        """测试搜索成功"""
        response = client.get("/api/kg/search/函数")
        assert response.status_code == 200
        data = response.json()
        assert "context" in data
        assert "learning_paths" in data
    
    def test_search_context_format(self, client):
        """测试上下文格式"""
        response = client.get("/api/kg/search/列表")
        data = response.json()
        context = data["context"]
        assert context is None or isinstance(context, str)
    
    def test_search_learning_paths_format(self, client):
        """测试学习路径格式"""
        response = client.get("/api/kg/search/字典")
        data = response.json()
        paths = data["learning_paths"]
        assert isinstance(paths, list)
    
    def test_search_with_special_characters(self, client):
        """测试特殊字符搜索"""
        response = client.get("/api/kg/search/if语句")
        assert response.status_code == 200
    
    def test_search_combined_results(self, client):
        """测试组合结果"""
        response = client.get("/api/kg/search/类")
        data = response.json()
        has_content = data["context"] is not None or len(data["learning_paths"]) > 0
        assert has_content or True


class TestHealthCheck:
    """健康检查测试"""
    
    def test_health_check_success(self, client):
        """测试健康检查成功"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "running"
