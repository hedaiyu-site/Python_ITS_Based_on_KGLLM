"""
响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    learning_path: Optional[str] = "basic"
    created_at: datetime
    is_active: bool = True


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool = True
    message: str = "登录成功"
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    """注册响应"""
    success: bool = True
    message: str = "注册成功"
    user: UserResponse


class ChatMessageResponse(BaseModel):
    """单条聊天消息"""
    id: int
    role: str
    content: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""
    success: bool = True
    session_id: str
    messages: List[ChatMessageResponse] = Field(default_factory=list)


class ChatSessionResponse(BaseModel):
    """会话信息"""
    session_id: str
    title: str
    started_at: str
    last_message_at: str
    message_count: int


class SessionListResponse(BaseModel):
    """会话列表响应"""
    success: bool = True
    sessions: List[ChatSessionResponse] = Field(default_factory=list)


class RecentHistoryResponse(BaseModel):
    """最近聊天记录响应"""
    success: bool = True
    messages: List[ChatMessageResponse] = Field(default_factory=list)


class DeleteSessionResponse(BaseModel):
    """删除会话响应"""
    success: bool = True
    message: str = "会话删除成功"


class ClearHistoryResponse(BaseModel):
    """清空历史响应"""
    success: bool = True
    message: str = "已清空所有聊天记录"
    deleted_count: int = 0


class QuizResponse(BaseModel):
    """测验响应"""
    success: bool = True
    question: str
    options: List[str] = Field(default_factory=list)
    answer: str
    explanation: str


class SearchResponse(BaseModel):
    """搜索响应"""
    success: bool = True
    context: Optional[str] = None
    learning_paths: List[Dict[str, Any]] = Field(default_factory=list)


class TopicsResponse(BaseModel):
    """主题列表响应"""
    success: bool = True
    topics: List[str] = Field(default_factory=list)


class StatisticsResponse(BaseModel):
    """统计信息响应"""
    success: bool = True
    nodes: int
    relations: int


class LearningPathResponse(BaseModel):
    """学习路径响应"""
    success: bool = True
    paths: List[Dict[str, Any]] = Field(default_factory=list)


class CourseOutlineResponse(BaseModel):
    """课程大纲响应"""
    success: bool = True
    course: Optional[str] = None
    chapters: List[Dict[str, Any]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class LearningProgressResponse(BaseModel):
    """学习进度响应"""
    success: bool = True
    learning_path: str
    total_knowledge_points: int = 0
    mastered_count: int = 0
    learning_count: int = 0
    progress_percentage: float = 0.0
    avg_mastery_level: float = 0.0
    knowledge_points: List[Dict[str, Any]] = Field(default_factory=list)


class KnowledgePointProgressResponse(BaseModel):
    """知识点进度响应"""
    success: bool = True
    message: str = ""
    knowledge_point_id: Optional[str] = None
    knowledge_point_name: Optional[str] = None
    status: Optional[str] = None
    mastery_level: Optional[int] = None
    quiz_score: Optional[float] = None
    quiz_count: Optional[int] = None
    correct_count: Optional[int] = None
    last_study_time: Optional[str] = None


class QuizQuestionResponse(BaseModel):
    """测验题目"""
    id: int
    question: str
    options: List[str] = Field(default_factory=list)
    answer: str


class QuizQuestionsResponse(BaseModel):
    """测验题目列表响应"""
    success: bool = True
    knowledge_point_id: str
    questions: List[QuizQuestionResponse] = Field(default_factory=list)


class SubmitAnswerRequest(BaseModel):
    """提交答案请求"""
    knowledge_point_id: str
    knowledge_point_name: str
    question_id: int
    user_answer: str


class SubmitAnswerResponse(BaseModel):
    """提交答案响应"""
    success: bool = True
    is_correct: bool
    correct_answer: str
    explanation: str
    your_answer: str


class QuizStatisticsResponse(BaseModel):
    """测验统计响应"""
    success: bool = True
    message: str = ""
    quiz_count: int = 0
    correct_count: int = 0
    accuracy: float = 0.0
    mastery_level: int = 0
    recent_history: List[Dict[str, Any]] = Field(default_factory=list)


class GenerateQuestionsResponse(BaseModel):
    """生成题目响应"""
    success: bool = True
    message: str
    existing_count: int = 0
    generated_count: int = 0


class QuizKnowledgePointResponse(BaseModel):
    """测验知识点项"""
    id: str
    name: str
    question_count: int = 0
    mastery_level: int = 0
    status: str = "not_started"


class QuizKnowledgePointsResponse(BaseModel):
    """测验知识点列表响应"""
    success: bool = True
    knowledge_points: List[QuizKnowledgePointResponse] = Field(default_factory=list)


class GraphNodeResponse(BaseModel):
    """图节点"""
    id: str
    name: str
    type: str
    parentId: Optional[str] = None


class GraphEdgeResponse(BaseModel):
    """图边"""
    source: str
    target: str
    type: str


class GraphDataResponse(BaseModel):
    """知识图谱可视化数据响应"""
    success: bool = True
    nodes: List[GraphNodeResponse] = Field(default_factory=list)
    edges: List[GraphEdgeResponse] = Field(default_factory=list)
