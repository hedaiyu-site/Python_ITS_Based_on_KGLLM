"""
大模型客户端模块(独立版本)

提供与阿里云Qwen大模型的交互功能
此版本用于独立运行，包含对话历史管理

主要功能:
- 同步/流式对话
- 对话历史管理
- 关键词提取
- 测验题目生成
- 代码解释和示例生成

依赖:
- openai: OpenAI兼容API客户端

配置:
- API_KEY: 阿里云DashScope API密钥
- BASE_URL: 阿里云兼容模式API地址
- MODEL_NAME: 使用的模型名称(qwen-plus)

作者: Python学习助手团队
版本: 1.0.0
"""

from openai import OpenAI
from typing import List, Dict, Optional
import json

API_KEY = "sk-b40dc8abd15446e1b36464a10be57eee"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen3.5-flash"


class LLMClient:
    """
    大模型客户端类
    
    封装与Qwen大模型的交互，支持对话历史管理
    """
    
    def __init__(self):
        """
        初始化客户端
        
        创建OpenAI客户端实例和对话历史列表
        """
        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.model = MODEL_NAME
        self.conversation_history = []
    
    def chat(self, message: str, context: str = "", system_prompt: str = None) -> str:
        """
        同步对话
        
        发送消息到大模型并获取完整回复，自动管理对话历史
        
        Args:
            message: 用户消息
            context: 知识图谱上下文(可选)
            system_prompt: 自定义系统提示词(可选)
        
        Returns:
            大模型的完整回复文本
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({
                "role": "system", 
                "content": f"以下是知识图谱中的相关信息，请参考这些信息回答问题：\n\n{context}"
            })
        
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        assistant_message = response.choices[0].message.content
        
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return assistant_message
    
    def chat_stream(self, message: str, context: str = "", system_prompt: str = None):
        """
        流式对话
        
        发送消息并以生成器形式逐块返回回复
        
        Args:
            message: 用户消息
            context: 知识图谱上下文(可选)
            system_prompt: 自定义系统提示词(可选)
        
        Yields:
            回复文本的每个片段
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({
                "role": "system", 
                "content": f"以下是知识图谱中的相关信息，请参考这些信息回答问题：\n\n{context}"
            })
        
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": message})
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": full_response})
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def clear_history(self):
        """清除对话历史"""
        self.conversation_history = []
    
    def _get_default_system_prompt(self) -> str:
        """
        获取默认系统提示词
        
        Returns:
            系统提示词字符串
        """
        return """你是一个专业的Python编程学习助手，你的任务是帮助用户学习Python编程。

你的特点：
1. 你拥有完整的Python知识体系，包括基础语法、数据类型、控制结构、函数、面向对象、模块、标准库、高级特性等内容
2. 你能够根据用户的问题，结合知识图谱中的信息，提供准确、详细的解答
3. 你善于用通俗易懂的语言解释复杂的编程概念
4. 你会提供代码示例来帮助用户理解
5. 你会根据用户的学习进度推荐合适的学习路径

回答问题时请注意：
- 如果知识图谱中有相关信息，请优先使用知识图谱中的内容
- 提供简洁明了的代码示例
- 解释概念时要循序渐进，由浅入深
- 如果用户是初学者，避免使用过于专业的术语
- 主动引导用户进行实践练习

请用中文回答所有问题。"""

    def extract_keywords(self, query: str) -> List[str]:
        """
        提取关键词
        
        使用大模型从查询中提取Python相关关键词
        
        Args:
            query: 用户查询文本
        
        Returns:
            关键词列表
        """
        extract_prompt = f"""请从以下问题中提取出Python相关的关键词，用于在知识图谱中搜索。
只返回关键词列表，用逗号分隔，不要有其他内容。

问题：{query}

关键词："""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0.3,
            max_tokens=100
        )
        
        keywords_str = response.choices[0].message.content.strip()
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        return keywords
    
    def generate_quiz(self, topic: str, difficulty: str = "medium") -> Dict:
        """
        生成测验题目
        
        根据主题和难度生成选择题
        
        Args:
            topic: 测验主题
            difficulty: 难度级别
        
        Returns:
            包含题目、选项、答案、解析的字典
        """
        prompt = f"""请为Python的"{topic}"知识点生成一道{difficulty}难度的练习题。

请按以下JSON格式返回：
{{
    "question": "题目内容",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "answer": "正确答案字母",
    "explanation": "答案解析"
}}

只返回JSON，不要有其他内容。"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "question": "生成题目失败",
                "options": [],
                "answer": "",
                "explanation": ""
            }
    
    def explain_code(self, code: str) -> str:
        """
        解释代码
        
        详细解释Python代码的功能和执行过程
        
        Args:
            code: Python代码字符串
        
        Returns:
            代码解释文本
        """
        prompt = f"""请详细解释以下Python代码的功能和执行过程：

```python
{code}
```

请逐行解释代码，并说明输出结果。"""
        
        return self.chat(prompt)
    
    def generate_code_example(self, concept: str) -> str:
        """
        生成代码示例
        
        为指定概念生成实用的代码示例
        
        Args:
            concept: Python概念名称
        
        Returns:
            包含注释的代码示例
        """
        prompt = f"""请为Python的"{concept}"概念生成一个实用的代码示例，并附带详细注释说明。"""
        return self.chat(prompt)


if __name__ == '__main__':
    """
    主函数
    
    测试大模型客户端功能
    """
    llm = LLMClient()
    
    print("测试大模型连接...")
    response = llm.chat("你好，请简单介绍一下你自己")
    print(f"回复: {response}")
    
    print("\n测试关键词提取...")
    keywords = llm.extract_keywords("如何使用Python的列表推导式创建一个新列表？")
    print(f"关键词: {keywords}")
