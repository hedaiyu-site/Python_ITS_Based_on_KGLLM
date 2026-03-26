"""
对话业务服务

提供对话、测验生成等业务逻辑
"""

from typing import List, Dict, AsyncGenerator, Optional
import asyncio
import logging

from app.ai.llm_service import LLMService
from app.repositories.neo4j.kg_repository import KnowledgeGraphRepository
from app.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)


class ChatService:
    """对话业务服务"""
    
    def __init__(
        self, 
        llm_service: LLMService, 
        kg_repository: KnowledgeGraphRepository,
        chat_history_service: Optional[ChatHistoryService] = None
    ):
        self._llm = llm_service
        self._kg_repo = kg_repository
        self._history_service = chat_history_service
    
    def chat(
        self, 
        message: str, 
        context: str = "",
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> tuple:
        """普通对话，返回(响应, session_id)"""
        if self._history_service:
            if not session_id:
                session_id = self._history_service.create_session()
            
            history_context = self._history_service.get_context_for_chat(user_id, session_id)
            self._history_service.save_user_message(user_id, session_id, message)
        else:
            history_context = []
        
        keywords = self._llm.extract_keywords(message)
        
        context_parts = []
        for msg in history_context[-6:]:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        for keyword in keywords[:2]:
            kg_context = self._search_kg_context(keyword)
            if kg_context:
                context_parts.append(kg_context)
        
        if context:
            context_parts.append(context)
        
        full_context = "\n\n".join(context_parts)
        response = self._llm.chat(message, full_context)
        
        if self._history_service and user_id and session_id:
            self._history_service.save_assistant_message(user_id, session_id, response)
        
        return response, session_id

    async def chat_stream(
        self, 
        message: str, 
        context: str = "",
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> tuple:
        """流式对话，返回(生成器, session_id)"""
        if self._history_service:
            if not session_id:
                session_id = self._history_service.create_session()
            
            history_context = self._history_service.get_context_for_chat(user_id, session_id)
            self._history_service.save_user_message(user_id, session_id, message)
        else:
            history_context = []
        
        loop = asyncio.get_event_loop()

        keywords = self._llm.extract_keywords(message)
        user_level = self._detect_user_level(message)

        if user_level == "intermediate":
            keywords = [kw for kw in keywords if '基础' not in kw and '入门' not in kw]

        should_show_path = any(kw in message for kw in [
            '学习路径', '怎么学', '学习顺序', '学习路线',
            '学习建议', '推荐学习', '进阶', '高级', '提升'
        ])

        context_parts = []
        for msg in history_context[-6:]:
            context_parts.append(f"{msg['role']}: {msg['content']}")

        context_tasks = []

        if should_show_path or user_level == "intermediate":
            context_tasks.append(self._get_learning_path_async(user_level))

        for keyword in keywords[:2]:
            context_tasks.append(loop.run_in_executor(None, self._search_kg_context, keyword))

        if context:
            context_tasks.append(asyncio.create_task(asyncio.sleep(0, result=context)))

        if context_tasks:
            results = await asyncio.gather(*context_tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, str) and r:
                    context_parts.append(r)

        full_context = "\n\n".join(context_parts) if context_parts else ""

        response_chunks = []
        async def stream_with_save():
            async for chunk in self._llm.chat_stream_async(message, full_context):
                response_chunks.append(chunk)
                yield chunk
            
            if self._history_service and user_id and session_id:
                full_response = "".join(response_chunks)
                self._history_service.save_assistant_message(user_id, session_id, full_response)

        return stream_with_save(), session_id
    
    def generate_quiz(self, topic: str) -> Dict:
        """生成测验题目"""
        return self._llm.generate_quiz(topic)
    
    def _search_kg_context(self, keyword: str) -> str:
        """搜索知识图谱上下文"""
        if not keyword:
            return ""
        
        nodes = self._kg_repo.search_nodes(keyword)
        
        context_parts = []
        for node in nodes:
            name = node['name']
            node_type = node['type']
            info = f"【{node_type}】{name}"
            
            for rel_info in node['relations'][:2]:
                if rel_info['children']:
                    info += f"\n  - {rel_info['rel']}: {', '.join(rel_info['children'])}"
            context_parts.append(info)
        
        return "\n\n".join(context_parts)
    
    async def _get_learning_path_async(self, level: str) -> str:
        """异步获取学习路径"""
        loop = asyncio.get_event_loop()
        basic_chapters = await loop.run_in_executor(
            None, self._kg_repo.get_chapters_by_course, "course_basic"
        )
        advanced_chapters = await loop.run_in_executor(
            None, self._kg_repo.get_chapters_by_course, "course_advanced"
        )
        
        if level == "beginner":
            path = "【Python初学者学习路径】\n\n"
            path += "建议按以下顺序学习基础课程：\n\n"
            path += "📚 Python基础编程教程\n"
            for i, ch in enumerate(basic_chapters, 1):
                path += f"   {i}. {ch}\n"
            path += "\n💡 学习建议：\n"
            path += "   - 每学完一章做练习巩固\n"
            path += "   - 重点掌握数据类型和流程控制\n"
            path += "   - 理解函数和面向对象概念\n"
            
        elif level == "intermediate":
            path = "【Python进阶学习路径】\n\n"
            path += "假设你已掌握Python基础，建议学习：\n\n"
            path += "📚 Python高级教程\n"
            for i, ch in enumerate(advanced_chapters, 1):
                path += f"   {i}. {ch}\n"
            path += "\n💡 学习建议：\n"
            path += "   - 深入学习标准库和并发编程\n"
            path += "   - 掌握网络编程和数据处理\n"
            path += "   - 尝试实际项目开发\n"
            
        else:
            path = "【Python完整学习路径】\n\n"
            path += "一、基础阶段\n"
            for i, ch in enumerate(basic_chapters, 1):
                path += f"   {i}. {ch}\n"
            path += "\n二、进阶阶段\n"
            for i, ch in enumerate(advanced_chapters, 1):
                path += f"   {i}. {ch}\n"
        
        return path
    
    def _detect_user_level(self, message: str) -> str:
        """检测用户水平"""
        message_lower = message.lower()
        
        beginner_keywords = ['初学者', '零基础', '入门', '新手', '刚开始', '基础', '小白', '从零开始']
        advanced_keywords = ['进阶', '高级', '深入', '高级教程', '提升', '进阶学习', '有基础', '学过', '掌握基础']
        
        for kw in advanced_keywords:
            if kw in message_lower:
                return "intermediate"
        
        for kw in beginner_keywords:
            if kw in message_lower:
                return "beginner"
        
        return "all"
