from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, JSON, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from config.settings import settings

# 创建SQLAlchemy引擎
DATABASE_URL = f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_db}"
engine = create_engine(DATABASE_URL)

# 创建会话本地类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础类
Base = declarative_base()

# 定义用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)  # 使用password而不是password_hash，与现有表结构匹配
    
    # 添加email列，设置默认值以允许现有行继续存在
    email = Column(String(100), unique=True, index=True, nullable=True, default=None)
    
    # 添加其他列，设置默认值以允许现有行继续存在
    level = Column(String(20), default="beginner")
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 定义学习进度模型
class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    node_id = Column(String(50), nullable=False)
    mastery_level = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 定义对话历史模型
class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    message_id = Column(String(50), nullable=False, unique=True)
    role = Column(String(20), nullable=False)  # user或assistant
    content = Column(String(10000), nullable=False)  # 增加长度限制到10000字符
    response_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 定义对话反馈模型
class ChatFeedback(Base):
    __tablename__ = "chat_feedback"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    response_id = Column(String(50), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 更新数据库表结构（添加缺少的列）
Base.metadata.create_all(bind=engine)

class UserDB:
    """用户数据访问"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def __del__(self):
        self.db.close()
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """获取用户信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "level": user.level,
                "preferences": user.preferences,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            }
        return {}
    
    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """根据用户名获取用户"""
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "password_hash": user.password,  # 返回password作为password_hash，保持与上层服务兼容
                "level": user.level,
                "preferences": user.preferences
            }
        return {}
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户"""
        user = User(
            username=user_data["username"],
            password=user_data["password_hash"],  # 使用password字段存储哈希后的密码
            email=user_data["email"],
            level=user_data.get("level", "beginner"),
            preferences=user_data.get("preferences", {})
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if "username" in user_data:
                user.username = user_data["username"]
            if "email" in user_data:
                user.email = user_data["email"]
            if "level" in user_data:
                user.level = user_data["level"]
            if "preferences" in user_data:
                user.preferences = user_data["preferences"]
            self.db.commit()
            self.db.refresh(user)
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "level": user.level,
                "preferences": user.preferences
            }
        return {}
    
    async def get_learning_progress(self, user_id: int, node_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取学习进度"""
        query = self.db.query(LearningProgress).filter(LearningProgress.user_id == user_id)
        if node_id:
            query = query.filter(LearningProgress.node_id == node_id)
        progress_list = query.all()
        return [{"id": p.id,
            "user_id": p.user_id,
            "node_id": p.node_id,
            "mastery_level": p.mastery_level,
            "completed": p.completed,
            "updated_at": p.updated_at.isoformat()
        } for p in progress_list]
    
    async def update_learning_progress(self, user_id: int, node_id: str, mastery_level: float, completed: bool) -> Dict[str, Any]:
        """更新学习进度"""
        progress = self.db.query(LearningProgress).filter(
            LearningProgress.user_id == user_id,
            LearningProgress.node_id == node_id
        ).first()
        
        if progress:
            progress.mastery_level = mastery_level
            progress.completed = completed
        else:
            progress = LearningProgress(
                user_id=user_id,
                node_id=node_id,
                mastery_level=mastery_level,
                completed=completed
            )
            self.db.add(progress)
        
        self.db.commit()
        self.db.refresh(progress)
        
        return {
            "id": progress.id,
            "user_id": progress.user_id,
            "node_id": progress.node_id,
            "mastery_level": progress.mastery_level,
            "completed": progress.completed
        }
    
    async def get_chat_history(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """获取对话历史"""
        history = self.db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).offset(offset).limit(limit).all()
        
        return [{
            "id": item.id,
            "message_id": item.message_id,
            "role": item.role,
            "content": item.content,
            "response_id": item.response_id,
            "created_at": item.created_at.isoformat()
        } for item in reversed(history)]  # 倒序返回，使最早的消息在前
    
    async def add_chat_message(self, user_id: int, message_id: str, role: str, content: str, response_id: str = None) -> Dict[str, Any]:
        """添加对话消息"""
        message = ChatHistory(
            user_id=user_id,
            message_id=message_id,
            role=role,
            content=content,
            response_id=response_id
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return {
            "id": message.id,
            "message_id": message.message_id,
            "role": message.role,
            "content": message.content,
            "response_id": message.response_id,
            "created_at": message.created_at.isoformat()
        }
    
    async def clear_chat_history(self, user_id: int) -> bool:
        """清空对话历史"""
        self.db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete()
        self.db.commit()
        return True
    
    async def submit_chat_feedback(self, response_id: str, rating: int, comment: str = None) -> Dict[str, Any]:
        """提交对话反馈"""
        feedback = ChatFeedback(
            response_id=response_id,
            rating=rating,
            comment=comment
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        return {
            "id": feedback.id,
            "response_id": feedback.response_id,
            "rating": feedback.rating,
            "comment": feedback.comment,
            "created_at": feedback.created_at.isoformat()
        }
    
    async def get_chat_history_count(self, user_id: int) -> int:
        """获取对话历史总数"""
        return self.db.query(ChatHistory).filter(ChatHistory.user_id == user_id).count()