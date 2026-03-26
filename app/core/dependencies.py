"""
依赖注入模块

提供各层实例的依赖注入
"""

from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.repositories.mysql.user_repository import UserRepository
from app.repositories.mysql.chat_history_repository import ChatHistoryRepository
from app.repositories.mysql.learning_path_repository import LearningPathRepository
from app.repositories.mysql.quiz_repository import QuizRepository
from app.repositories.neo4j.kg_repository import KnowledgeGraphRepository
from app.ai.llm_service import LLMService
from app.services.user_service import UserService
from app.services.kg_service import KnowledgeGraphService
from app.services.chat_service import ChatService
from app.services.chat_history_service import ChatHistoryService
from app.services.learning_path_service import LearningPathService
from app.services.quiz_service import QuizService
from app.core.config import settings

security = HTTPBearer()


@lru_cache()
def get_user_repository() -> UserRepository:
    """获取用户数据仓库"""
    return UserRepository(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE
    )


@lru_cache()
def get_chat_history_repository() -> ChatHistoryRepository:
    """获取聊天记录数据仓库"""
    repo = ChatHistoryRepository(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE
    )
    repo.create_table()
    return repo


@lru_cache()
def get_kg_repository() -> KnowledgeGraphRepository:
    """获取知识图谱数据仓库"""
    return KnowledgeGraphRepository(
        url=settings.NEO4J_URL,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
        database=settings.NEO4J_DATABASE
    )


@lru_cache()
def get_llm_service() -> LLMService:
    """获取大模型服务"""
    return LLMService(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model_name=settings.LLM_MODEL_NAME
    )


@lru_cache()
def get_user_service() -> UserService:
    """获取用户业务服务"""
    return UserService(
        user_repository=get_user_repository(),
        learning_path_service=get_learning_path_service()
    )


@lru_cache()
def get_kg_service() -> KnowledgeGraphService:
    """获取知识图谱业务服务"""
    return KnowledgeGraphService(kg_repository=get_kg_repository())


@lru_cache()
def get_chat_history_service() -> ChatHistoryService:
    """获取聊天记录业务服务"""
    return ChatHistoryService(chat_history_repository=get_chat_history_repository())


@lru_cache()
def get_chat_service() -> ChatService:
    """获取对话业务服务"""
    return ChatService(
        llm_service=get_llm_service(),
        kg_repository=get_kg_repository(),
        chat_history_service=get_chat_history_service()
    )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """从Token中获取当前用户ID"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的Token"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token"
        )


@lru_cache()
def get_learning_path_repository() -> LearningPathRepository:
    """获取学习路径数据仓库"""
    return LearningPathRepository(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE
    )


@lru_cache()
def get_quiz_repository() -> QuizRepository:
    """获取测验题目数据仓库"""
    return QuizRepository(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE
    )


@lru_cache()
def get_learning_path_service() -> LearningPathService:
    """获取学习路径业务服务"""
    return LearningPathService(
        learning_path_repository=get_learning_path_repository(),
        kg_repository=get_kg_repository()
    )


@lru_cache()
def get_quiz_service() -> QuizService:
    """获取测验业务服务"""
    return QuizService(
        quiz_repository=get_quiz_repository(),
        learning_path_repository=get_learning_path_repository(),
        llm_service=get_llm_service()
    )
