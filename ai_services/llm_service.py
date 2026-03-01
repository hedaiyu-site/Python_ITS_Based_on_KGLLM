from typing import Dict, Any, List, Optional
import time
from config.settings import settings
import openai

class LLMService:
    """大模型服务"""
    
    def __init__(self):
        """初始化大模型API连接"""
        # 配置OpenAI客户端
        self.client = openai.OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url
        )
        self.model = settings.llm_model
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """生成文本"""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            text = response.choices[0].message.content
            response_time = time.time() - start_time
            tokens_used = response.usage.total_tokens
            
            return {
                "text": text,
                "response_time": round(response_time, 2),
                "tokens_used": tokens_used
            }
        except Exception as e:
            print(f"大模型调用失败: {str(e)}")
            # 返回错误信息和默认值
            return {
                "text": f"错误: {str(e)}",
                "response_time": round(time.time() - start_time, 2),
                "tokens_used": 0
            }
    
    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """对话补全"""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            text = response.choices[0].message.content
            response_time = time.time() - start_time
            tokens_used = response.usage.total_tokens
            
            return {
                "text": text,
                "response_time": round(response_time, 2),
                "tokens_used": tokens_used
            }
        except Exception as e:
            print(f"对话补全失败: {str(e)}")
            # 返回错误信息和默认值
            return {
                "text": f"错误: {str(e)}",
                "response_time": round(time.time() - start_time, 2),
                "tokens_used": 0
            }
    
    async def embedding(self, text: str) -> List[float]:
        """生成文本向量"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # 使用适合的嵌入模型
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"向量生成失败: {str(e)}")
            # 返回默认向量
            return [0.0] * 1536  # text-embedding-3-small的向量维度
    
    async def batch_embedding(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本向量"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # 使用适合的嵌入模型
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"批量向量生成失败: {str(e)}")
            # 返回默认向量
            return [[0.0] * 1536 for _ in texts]