from typing import List, Dict, Any
import uuid
import time
from config.settings import settings
from data.user_db import UserDB
from services.knowledge_service import KnowledgeService
from services.knowledge_vector_service import get_knowledge_vector_service
from openai import OpenAI


class ChatService:
    """对话管理服务"""
    
    def __init__(self):
        self.user_db = UserDB()
        self.knowledge_service = KnowledgeService()
        self.vector_service = get_knowledge_vector_service()
        
        self.llm_client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url
        )
        self.llm_model = settings.llm_model
        
        self.use_vector_search = True
        self.use_graph_search = True
    
    async def ask_question(self, user_id: int, question: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理用户提问"""
        start_time = time.time()
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        
        try:
            await self.user_db.add_chat_message(
                user_id=user_id,
                message_id=message_id,
                role="user",
                content=question
            )
            
            knowledge_sources = []
            knowledge_context = ""
            
            try:
                if self.use_vector_search:
                    vector_results = await self._search_by_vector(question)
                    if vector_results:
                        knowledge_sources.extend([r['source'] for r in vector_results])
                        knowledge_context += self._build_context_from_results(vector_results, "语义搜索结果")
                
                if self.use_graph_search:
                    graph_results = await self._search_by_graph(question)
                    if graph_results:
                        new_sources = [r['source'] for r in graph_results if r['source'] not in knowledge_sources]
                        knowledge_sources.extend(new_sources)
                        knowledge_context += self._build_context_from_results(graph_results, "知识图谱结果")
                        
            except Exception as e:
                print(f"搜索知识时出错: {str(e)}")
            
            messages = [
                {"role": "system", "content": "你是一个智能学习助手，专注于帮助用户解答与学习相关的问题。请提供准确、详细的回答。如果有知识图谱的相关信息，请优先参考这些信息进行回答。"}
            ]
            
            if knowledge_context:
                messages.append({"role": "system", "content": knowledge_context})
            
            for item in context:
                messages.append({"role": item.get("role", "user"), "content": item.get("content", "")})
            
            messages.append({"role": "user", "content": question})
            
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            
            await self.user_db.add_chat_message(
                user_id=user_id,
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=answer,
                response_id=response_id
            )
            
            response_time = round(time.time() - start_time, 2)
            
            return {
                "response_id": response_id,
                "answer": answer,
                "knowledge_sources": knowledge_sources,
                "response_time": response_time
            }
            
        except Exception as e:
            error_message = f"处理问题时出错: {str(e)}"
            print(error_message)
            
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
    
    async def _search_by_vector(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """使用向量搜索获取相关知识"""
        try:
            results = await self.vector_service.semantic_search(query, top_k=top_k, min_score=0.3)
            
            formatted_results = []
            for result in results:
                metadata = result.get('metadata', {})
                formatted_results.append({
                    'source': f"{metadata.get('name', 'N/A')} (ID: {metadata.get('node_id', 'N/A')})",
                    'name': metadata.get('name', ''),
                    'content': metadata.get('name', ''),
                    'score': result.get('score', 0),
                    'type': 'vector'
                })
            
            return formatted_results
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []
    
    async def _search_by_graph(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """使用知识图谱搜索获取相关知识"""
        try:
            results = await self.knowledge_service.search(query, limit=limit)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'source': f"{result['name']} (ID: {result['node_id']})",
                    'name': result['name'],
                    'content': result.get('content', ''),
                    'node_type': result.get('node_type', ''),
                    'type': 'graph'
                })
            
            return formatted_results
        except Exception as e:
            print(f"图谱搜索失败: {e}")
            return []
    
    def _build_context_from_results(self, results: List[Dict[str, Any]], source_name: str) -> str:
        """构建知识上下文"""
        if not results:
            return ""
        
        context = f"\n{source_name}:\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result.get('name', 'N/A')}"
            if result.get('content'):
                content = result['content']
                if len(content) > 200:
                    content = content[:200] + "..."
                context += f": {content}"
            context += "\n"
        
        return context
    
    async def get_history(self, user_id: int, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """获取对话历史"""
        try:
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
            if rating < 1 or rating > 5:
                return {
                    "error": "评分必须在1-5之间",
                    "response_id": response_id
                }
            
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
