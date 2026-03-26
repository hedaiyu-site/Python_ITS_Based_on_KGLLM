"""
知识图谱模块测试
"""

import pytest


class TestKGStatistics:
    """知识图谱统计测试"""
    
    def test_get_statistics_success(self, client):
        """测试获取统计信息成功"""
        response = client.get("/api/kg/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "nodes" in data
        assert "relations" in data
        assert isinstance(data["nodes"], int)
        assert isinstance(data["relations"], int)
    
    def test_statistics_response_format(self, client):
        """测试统计响应格式"""
        response = client.get("/api/kg/statistics")
        data = response.json()
        assert data["nodes"] == 100
        assert data["relations"] == 200


class TestKGTopics:
    """知识点主题测试"""
    
    def test_get_topics_success(self, client):
        """测试获取主题列表成功"""
        response = client.get("/api/kg/topics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "topics" in data
        assert isinstance(data["topics"], list)
    
    def test_topics_not_empty(self, client):
        """测试主题列表不为空"""
        response = client.get("/api/kg/topics")
        data = response.json()
        assert len(data["topics"]) > 0


class TestKGOutline:
    """课程大纲测试"""
    
    def test_get_basic_outline_success(self, client):
        """测试获取基础课程大纲"""
        response = client.get("/api/kg/outline/basic")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "course" in data
        assert "chapters" in data
    
    def test_get_advanced_outline_success(self, client):
        """测试获取高级课程大纲"""
        response = client.get("/api/kg/outline/advanced")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_outline_invalid_course_type(self, client):
        """测试无效课程类型返回422"""
        response = client.get("/api/kg/outline/invalid")
        assert response.status_code == 422
    
    def test_outline_chapters_format(self, client):
        """测试章节格式"""
        response = client.get("/api/kg/outline/basic")
        data = response.json()
        chapters = data["chapters"]
        assert isinstance(chapters, list)
        if len(chapters) > 0:
            chapter = chapters[0]
            assert "order" in chapter or "chapter" in chapter


class TestKGLearningPath:
    """学习路径测试"""
    
    def test_get_learning_path_success(self, client):
        """测试获取学习路径成功"""
        response = client.get("/api/kg/path/函数")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "paths" in data
    
    def test_learning_path_with_topic(self, client):
        """测试特定主题学习路径"""
        response = client.get("/api/kg/path/列表")
        data = response.json()
        assert isinstance(data["paths"], list)


class TestKGSearch:
    """知识搜索测试"""
    
    def test_search_knowledge_success(self, client):
        """测试搜索知识点成功"""
        response = client.get("/api/search/函数")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "context" in data
        assert "learning_paths" in data
    
    def test_search_returns_context(self, client):
        """测试搜索返回上下文"""
        response = client.get("/api/search/列表")
        data = response.json()
        assert data["context"] is not None or data["learning_paths"] is not None
