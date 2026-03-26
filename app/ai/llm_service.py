"""
大模型AI服务

提供与阿里云Qwen大模型的交互功能
"""

from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Optional, AsyncGenerator, Generator
import json
import asyncio
import re
import logging

logger = logging.getLogger(__name__)

PYTHON_KEYWORDS = [
    '列表', '字典', '元组', '集合', '字符串', '数字', '整数', '浮点数',
    '函数', '类', '对象', '模块', '包', '装饰器', '生成器', '迭代器',
    'if', 'else', 'for', 'while', 'try', 'except', 'with', 'class', 'def',
    'import', 'from', 'return', 'yield', 'lambda', 'async', 'await',
    'print', 'input', 'open', 'range', 'len', 'type', 'list', 'dict', 'set',
    '继承', '多态', '封装', '面向对象', '异常', '文件', '线程', '进程',
    '正则', '表达式', '推导式', '切片', '索引', '变量', '常量', '参数',
    'sys', 'os', 'math', 'json', 'datetime', 'random', 're', 'threading',
    'requests', 'BeautifulSoup', 'Scrapy', 'selenium', 'pandas', 'numpy'
]


class LLMService:
    """
    大模型服务
    
    封装与Qwen大模型的交互
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model_name: str = "qwen-plus",
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens
        logger.info(f"初始化大模型服务: {base_url}, 模型: {model_name}")
    
    def chat(self, message: str, context: str = "", system_prompt: str = None) -> str:
        """同步对话"""
        messages = self._build_messages(message, context, system_prompt)
        
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens
        )
        return response.choices[0].message.content
    
    def chat_stream(self, message: str, context: str = "", system_prompt: str = None) -> Generator[str, None, None]:
        """同步流式对话"""
        messages = self._build_messages(message, context, system_prompt)
        
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def chat_stream_async(self, message: str, context: str = "", system_prompt: str = None) -> AsyncGenerator[str, None]:
        """异步流式对话"""
        messages = self._build_messages(message, context, system_prompt)
        
        stream = await self._async_client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def extract_keywords(self, query: str, max_keywords: int = 2) -> List[str]:
        """提取关键词"""
        keywords = []
        query_lower = query.lower()
        
        for kw in PYTHON_KEYWORDS:
            if kw.lower() in query_lower:
                keywords.append(kw)
                if len(keywords) >= max_keywords:
                    break
        
        if not keywords:
            words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', query)
            keywords = [w for w in words if len(w) > 1][:max_keywords]
        
        return keywords
    
    def generate_quiz(self, topic: str) -> Dict:
        """生成测验题目"""
        prompt = f"""为Python的"{topic}"生成一道选择题，JSON格式返回：
{{"question":"题目","options":["A.选项1","B.选项2","C.选项3","D.选项4"],"answer":"A","explanation":"解析"}}"""
        
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"生成测验题目失败: {e}")
            return {"question": "生成失败", "options": [], "answer": "", "explanation": ""}
    
    def _build_messages(self, message: str, context: str = "", system_prompt: str = None) -> List[Dict]:
        """构建消息列表"""
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"参考以下知识图谱信息回答问题：\n\n{context}"
            })
        
        messages.append({"role": "user", "content": message})
        return messages
    
    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词"""
        return """你是Python编程学习助手。回答要求：
1. 简洁明了，直接回答问题
2. 提供代码示例时用```python包裹
3. 控制回答长度，突出重点
4. 用中文回答
5. 如果提供了知识图谱中的学习路径信息，请优先使用并展示给用户"""
