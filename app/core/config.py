"""
配置管理模块

使用pydantic-settings管理应用配置
支持从.env文件和环境变量加载配置
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    APP_NAME: str = "Python学习助手API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于知识图谱+大模型的Python学习系统"
    DEBUG: bool = False
    
    NEO4J_URL: str = Field(default="bolt://localhost:7687", alias="NEO4J_URL")
    NEO4J_USER: str = Field(default="neo4j", alias="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="your_neo4j_password", alias="NEO4J_PASSWORD")
    NEO4J_DATABASE: str = Field(default="neo4j", alias="NEO4J_DATABASE")
    
    LLM_API_KEY: str = Field(default="your_api_key", alias="LLM_API_KEY")
    LLM_BASE_URL: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", alias="LLM_BASE_URL")
    LLM_MODEL_NAME: str = Field(default="qwen-plus", alias="LLM_MODEL_NAME")
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1500
    
    MYSQL_HOST: str = Field(default="localhost", alias="MYSQL_HOST")
    MYSQL_PORT: int = Field(default=3306, alias="MYSQL_PORT")
    MYSQL_USER: str = Field(default="root", alias="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(default="your_mysql_password", alias="MYSQL_PASSWORD")
    MYSQL_DATABASE: str = Field(default="python_learning", alias="MYSQL_DATABASE")
    
    JWT_SECRET_KEY: str = Field(default="your-jwt-secret-key-change-in-production", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置实例(单例)
    
    使用lru_cache确保配置只加载一次
    """
    return Settings()


settings = get_settings()
