"""
API测试配置

提供测试fixtures和mock对象
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def create_mock_user_repository():
    repo = MagicMock()
    repo.exists_by_username.return_value = False
    repo.exists_by_email.return_value = False
    repo.create.return_value = 1
    repo.find_by_username.return_value = {
        "id": 1,
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com",
        "created_at": "2024-01-01 00:00:00",
        "is_active": True
    }
    repo.find_by_id.return_value = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01 00:00:00",
        "is_active": True
    }
    return repo


def create_mock_kg_repository():
    repo = MagicMock()
    repo.get_statistics.return_value = {"nodes": 100, "relations": 200}
    repo.get_all_topics.return_value = ["函数", "列表", "字典", "类", "模块"]
    repo.get_course_outline.return_value = {
        "course": "Python基础编程教程",
        "chapters": [
            {"order": "1", "chapter": "Python基础", "sections": ["变量", "数据类型"]},
            {"order": "2", "chapter": "流程控制", "sections": ["if语句", "循环"]}
        ]
    }
    repo.get_learning_path_by_topic.return_value = [
        {"course": "Python基础编程教程", "chapter": "Python基础", "section": "函数"}
    ]
    repo.search_nodes.return_value = [
        {
            "name": "函数",
            "type": "Section",
            "relations": [{"rel": "HAS_SECTION", "children": ["参数", "返回值"]}]
        }
    ]
    repo.get_chapters_by_course.return_value = ["Python基础", "流程控制", "函数"]
    repo.close.return_value = None
    return repo


def create_mock_llm_service():
    service = MagicMock()
    service.chat.return_value = "这是测试回复"
    service.extract_keywords.return_value = ["函数"]
    service.generate_quiz.return_value = {
        "question": "Python中如何定义函数？",
        "options": ["A. def", "B. function", "C. func", "D. define"],
        "answer": "A",
        "explanation": "Python使用def关键字定义函数"
    }
    
    async def mock_stream(*args, **kwargs):
        for chunk in ["这", "是", "测", "试"]:
            yield chunk
    
    service.chat_stream_async = mock_stream
    return service


def create_mock_chat_history_repository():
    repo = MagicMock()
    repo.save_message.return_value = 1
    repo.get_session_history.return_value = []
    repo.get_user_sessions.return_value = []
    repo.get_recent_history.return_value = []
    repo.get_session_first_message.return_value = None
    repo.delete_session.return_value = 1
    repo.clear_user_history.return_value = 0
    repo.create_table.return_value = None
    return repo


@pytest.fixture
def mock_user_repository():
    return create_mock_user_repository()


@pytest.fixture
def mock_kg_repository():
    return create_mock_kg_repository()


@pytest.fixture
def mock_llm_service():
    return create_mock_llm_service()


@pytest.fixture
def mock_chat_history_repository():
    return create_mock_chat_history_repository()


@pytest.fixture
def client():
    from fastapi import FastAPI
    from app.api.routers import auth_router, kg_router, chat_router, history_router, learning_path_router, quiz_router
    from app.api.schemas.responses import HealthResponse
    from app.services.user_service import UserService
    from app.services.kg_service import KnowledgeGraphService
    from app.services.chat_service import ChatService
    from app.services.chat_history_service import ChatHistoryService
    from app.core.exceptions import AppException, app_exception_handler, http_exception_handler
    
    mock_user_repo = create_mock_user_repository()
    mock_kg_repo = create_mock_kg_repository()
    mock_llm = create_mock_llm_service()
    mock_history_repo = create_mock_chat_history_repository()
    
    mock_user_service = UserService(user_repository=mock_user_repo)
    mock_kg_service = KnowledgeGraphService(kg_repository=mock_kg_repo)
    mock_history_service = ChatHistoryService(chat_history_repository=mock_history_repo)
    mock_chat_service = ChatService(
        llm_service=mock_llm, 
        kg_repository=mock_kg_repo,
        chat_history_service=mock_history_service
    )
    
    test_app = FastAPI(title="Python学习助手API测试")
    
    test_app.add_exception_handler(AppException, app_exception_handler)
    test_app.add_exception_handler(HTTPException, http_exception_handler)
    
    test_app.dependency_overrides = {}
    
    from app.core.dependencies import get_user_service, get_kg_service, get_chat_service, get_chat_history_service
    
    test_app.dependency_overrides[get_user_service] = lambda: mock_user_service
    test_app.dependency_overrides[get_kg_service] = lambda: mock_kg_service
    test_app.dependency_overrides[get_chat_service] = lambda: mock_chat_service
    test_app.dependency_overrides[get_chat_history_service] = lambda: mock_history_service
    
    test_app.include_router(auth_router, prefix="/api")
    test_app.include_router(kg_router, prefix="/api")
    test_app.include_router(chat_router, prefix="/api")
    test_app.include_router(history_router, prefix="/api")
    test_app.include_router(learning_path_router, prefix="/api")
    test_app.include_router(quiz_router, prefix="/api")
    
    @test_app.get("/")
    async def root():
        return {"message": "Python学习助手API", "version": "1.0.0", "status": "running"}
    
    @test_app.get("/health", response_model=HealthResponse)
    async def health_check():
        return HealthResponse(status="healthy", version="1.0.0")
    
    with TestClient(test_app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    from app.core.config import settings
    import jwt
    from datetime import datetime, timedelta
    
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        {"user_id": 1, "username": "testuser", "exp": expiration},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return {"Authorization": f"Bearer {token}"}
