from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 基本配置
    app_name: str = "毕设后端API服务"
    debug: bool = True
    version: str = "1.0.0"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 数据库配置
    # Neo4j配置
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "hedaiyu123"
    
    # MySQL配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "finnal_project"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # 向量数据库配置
    vector_db_type: str = "faiss"  # 可选: faiss, milvus
    vector_db_path: str = "./vector_db"
    
    # 大模型配置
    llm_api_key: str = "your_api_key"
    llm_base_url: str = "https://api.example.com/v1"
    llm_model: str = "gpt-3.5-turbo"
    
    # 安全配置
    secret_key: str = "your_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS配置
    allow_origins: list = ["*"]
    allow_credentials: bool = True
    allow_methods: list = ["*"]
    allow_headers: list = ["*"]
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建配置实例
settings = Settings()