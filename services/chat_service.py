from typing import List, Dict, Any
import uuid
import time
from config.settings import settings
from data.user_db import UserDB
from services.knowledge_service import KnowledgeService
from openai import OpenAI

class ChatService:
    """对话管理服务"""
    
    def __init__(self):
        """初始化对话服务"""
        # 初始化数据库连接
        self.user_db = UserDB()
        
        # 初始化知识图谱服务
        self.knowledge_service = KnowledgeService()
        
        # 初始化大模型客户端
        self.llm_client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url
        )
        self.llm_model = settings.llm_model
    
    async def ask_question(self, user_id: int, question: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理用户提问"""
        start_time = time.time()
        
        # 生成唯一ID
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        try:
            # 保存用户问题
            await self.user_db.add_chat_message(
                user_id=user_id,
                message_id=message_id,
                role="user",
                content=question
            )
            
            # 从知识图谱中获取相关信息
            knowledge_sources = []
            knowledge_context = ""
            
            try:
                # 搜索知识图谱中与问题相关的节点
                search_results = await self.knowledge_service.search(question, limit=5)
                
                if search_results:
                    knowledge_sources = [f"{result['name']} (ID: {result['node_id']})" for result in search_results]
                    
                    # 构建知识图谱上下文
                    knowledge_context = "基于知识图谱的相关信息:\n"
                    for i, result in enumerate(search_results, 1):
                        knowledge_context += f"{i}. {result['name']}: {result.get('content', '无详细内容')}\n"
            except Exception as e:
                print(f"从知识图谱获取信息时出错: {str(e)}")
                # 出错时继续执行，使用大模型的默认能力
            
            # 构建大模型请求
            messages = [
                {"role": "system", "content": "你是一个智能学习助手，专注于帮助用户解答与学习相关的问题。请提供准确、详细的回答。如果有知识图谱的相关信息，请优先参考这些信息进行回答。"}
            ]
            
            # 添加知识图谱上下文（如果有）
            if knowledge_context:
                messages.append({"role": "system", "content": knowledge_context})
            
            # 添加上下文（如果有）
            for item in context:
                messages.append({"role": item.get("role", "user"), "content": item.get("content", "")})
            
            # 添加用户最新问题
            messages.append({"role": "user", "content": question})
            
            # 调用大模型
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # 获取大模型回答
            answer = response.choices[0].message.content.strip()
            
            # 保存助手回答
            await self.user_db.add_chat_message(
                user_id=user_id,
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=answer,
                response_id=response_id
            )
            
            # 计算响应时间
            response_time = round(time.time() - start_time, 2)
            
            return {
                "response_id": response_id,
                "answer": answer,
                "knowledge_sources": knowledge_sources,  # 从知识图谱中获取的相关来源
                "response_time": response_time
            }
            
        except Exception as e:
            # 出错时返回错误信息
            error_message = f"处理问题时出错: {str(e)}"
            print(error_message)
            
            # 保存错误信息
            await self.user_db.add_chat_message(
                user_id=user_id,
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=error_message,
                response_id=response_id
            )
            
            return {
                "response_id": response_id,
                "answer": error_message,
                "knowledge_sources": [],
                "response_time": round(time.time() - start_time, 2)
            }
    
    async def get_history(self, user_id: int, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取对话历史"""
        try:
            # 获取对话历史
            history = await self.user_db.get_chat_history(user_id, limit, offset)
            total = await self.user_db.get_chat_history_count(user_id)
            
            return {
                "user_id": user_id,
                "history": history,
                "total": total
            }
        except Exception as e:
            print(f"获取对话历史时出错: {str(e)}")
            return {
                "user_id": user_id,
                "history": [],
                "total": 0
            }
    
    async def submit_feedback(self, response_id: str, rating: int, comment: str = None) -> Dict[str, Any]:
        """提交反馈"""
        try:
            # 验证评分范围
            if rating < 1 or rating > 5:
                return {
                    "error": "评分必须在1-5之间",
                    "response_id": response_id
                }
            
            # 保存反馈
            feedback = await self.user_db.submit_chat_feedback(response_id, rating, comment)
            
            return {
                "response_id": response_id,
                "rating": rating,
                "comment": comment,
                "message": "反馈提交成功"
            }
        except Exception as e:
            print(f"提交反馈时出错: {str(e)}")
            return {
                "error": "提交反馈失败",
                "response_id": response_id
            }
    
    async def clear_history(self, user_id: int) -> Dict[str, Any]:
        """清空对话历史"""
        try:
            # 清空对话历史
            success = await self.user_db.clear_chat_history(user_id)
            
            if success:
                return {
                    "user_id": user_id,
                    "message": "对话历史已清空"
                }
            else:
                return {
                    "user_id": user_id,
                    "error": "清空对话历史失败"
                }
        except Exception as e:
            print(f"清空对话历史时出错: {str(e)}")
            return {
                "user_id": user_id,
                "error": "清空对话历史失败"
            }