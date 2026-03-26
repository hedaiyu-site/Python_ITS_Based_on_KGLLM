"""
Python学习助手模块(独立版本)

结合知识图谱和大模型的Python学习助手
提供命令行交互式学习体验

主要功能:
- 问题分类处理(概念、代码、路径、练习、测验)
- 知识图谱上下文检索
- 学习路径推荐
- 交互式命令行界面

依赖:
- kg_retriever: 知识图谱检索器
- llm_client: 大模型客户端

作者: Python学习助手团队
版本: 1.0.0
"""

from kg_retriever import KnowledgeGraphRetriever
from llm_client import LLMClient
from typing import Dict, List, Optional
import re


class PythonLearningAssistant:
    """
    Python学习助手类
    
    整合知识图谱和大模型，提供智能学习辅助功能
    """
    
    def __init__(self):
        """
        初始化学习助手
        
        创建知识图谱检索器和大模型客户端实例
        """
        self.kg_retriever = KnowledgeGraphRetriever()
        self.llm_client = LLMClient()
        self.user_level = "beginner"
        self.current_topic = None
    
    def close(self):
        """关闭资源连接"""
        self.kg_retriever.close()
    
    def ask(self, question: str) -> str:
        """
        回答用户问题
        
        根据问题类型自动分类并调用相应的处理方法
        
        Args:
            question: 用户问题
        
        Returns:
            回答内容
        """
        question_type = self._classify_question(question)
        
        if question_type == "concept":
            return self._handle_concept_question(question)
        elif question_type == "code":
            return self._handle_code_question(question)
        elif question_type == "path":
            return self._handle_path_question(question)
        elif question_type == "practice":
            return self._handle_practice_question(question)
        elif question_type == "quiz":
            return self._handle_quiz_question(question)
        else:
            return self._handle_general_question(question)
    
    def _classify_question(self, question: str) -> str:
        """
        分类问题类型
        
        根据关键词判断问题属于哪种类型
        
        Args:
            question: 用户问题
        
        Returns:
            问题类型: concept, code, path, practice, quiz, general
        """
        question_lower = question.lower()
        
        if any(kw in question_lower for kw in ['什么是', '解释', '概念', '介绍', '讲解']):
            return "concept"
        elif any(kw in question_lower for kw in ['代码', '怎么写', '如何实现', '示例', '例子']):
            return "code"
        elif any(kw in question_lower for kw in ['学习路径', '怎么学', '学习顺序', '先学', '路线']):
            return "path"
        elif any(kw in question_lower for kw in ['练习', '实战', '项目', '动手']):
            return "practice"
        elif any(kw in question_lower for kw in ['题目', '测验', '测试', '考考']):
            return "quiz"
        else:
            return "general"
    
    def _handle_concept_question(self, question: str) -> str:
        """
        处理概念类问题
        
        Args:
            question: 用户问题
        
        Returns:
            概念解释
        """
        keywords = self.llm_client.extract_keywords(question)
        
        context_parts = []
        for keyword in keywords[:3]:
            kg_context = self.kg_retriever.get_knowledge_context(keyword)
            if kg_context:
                context_parts.append(kg_context)
        
        context = "\n\n".join(context_parts)
        
        related = []
        for keyword in keywords[:2]:
            related.extend(self.kg_retriever.get_related_concepts(keyword))
        
        if related:
            context += "\n\n相关概念：\n"
            for r in related[:5]:
                context += f"- {r['type']}: {r['name']}\n"
        
        return self.llm_client.chat(question, context)
    
    def _handle_code_question(self, question: str) -> str:
        """
        处理代码类问题
        
        Args:
            question: 用户问题
        
        Returns:
            代码示例和解释
        """
        keywords = self.llm_client.extract_keywords(question)
        
        context = ""
        for keyword in keywords[:2]:
            kg_context = self.kg_retriever.get_knowledge_context(keyword)
            if kg_context:
                context += kg_context + "\n\n"
        
        system_prompt = """你是一个Python编程专家，请根据用户的问题提供代码示例。
要求：
1. 代码要简洁、规范、有注释
2. 解释代码的执行过程
3. 提供可能的输出结果
4. 如果有多种实现方式，可以简要对比

请用中文回答。"""
        
        return self.llm_client.chat(question, context, system_prompt)
    
    def _handle_path_question(self, question: str) -> str:
        """
        处理学习路径类问题
        
        Args:
            question: 用户问题
        
        Returns:
            学习路径推荐
        """
        keywords = self.llm_client.extract_keywords(question)
        
        paths = []
        for keyword in keywords[:3]:
            path = self.kg_retriever.get_learning_path(keyword)
            paths.extend(path)
        
        basic_structure = self.kg_retriever.get_course_structure("basic")
        advanced_structure = self.kg_retriever.get_course_structure("advanced")
        
        context = "Python学习路径：\n\n"
        context += "【基础课程】\n"
        for ch in basic_structure['chapters']:
            context += f"  {ch['chapter']}\n"
        
        context += "\n【高级课程】\n"
        for ch in advanced_structure['chapters']:
            context += f"  {ch['chapter']}\n"
        
        if paths:
            context += "\n【相关学习路径】\n"
            for p in paths[:5]:
                context += f"  {p['course']} > {p['chapter']} > {p['section']}\n"
        
        system_prompt = """你是一个Python学习顾问，请根据知识图谱中的课程结构，
为用户推荐合适的学习路径。考虑用户的基础水平，给出循序渐进的学习建议。"""
        
        return self.llm_client.chat(question, context, system_prompt)
    
    def _handle_practice_question(self, question: str) -> str:
        """
        处理练习类问题
        
        Args:
            question: 用户问题
        
        Returns:
            练习建议和代码框架
        """
        keywords = self.llm_client.extract_keywords(question)
        
        context = ""
        for keyword in keywords[:2]:
            kg_context = self.kg_retriever.get_knowledge_context(keyword)
            if kg_context:
                context += kg_context + "\n\n"
        
        system_prompt = """你是一个Python编程教练，请为用户设计实践练习。
要求：
1. 练习要贴近实际应用场景
2. 难度适中，循序渐进
3. 提供清晰的练习目标
4. 给出参考代码框架
5. 提示可能遇到的问题

请用中文回答。"""
        
        return self.llm_client.chat(question, context, system_prompt)
    
    def _handle_quiz_question(self, question: str) -> str:
        """
        处理测验类问题
        
        Args:
            question: 用户问题
        
        Returns:
            测验题目和答案
        """
        keywords = self.llm_client.extract_keywords(question)
        topic = keywords[0] if keywords else "Python基础"
        
        quiz = self.llm_client.generate_quiz(topic, "medium")
        
        response = f"📝 练习题：{quiz['question']}\n\n"
        for opt in quiz['options']:
            response += f"{opt}\n"
        response += f"\n正确答案：{quiz['answer']}\n"
        response += f"解析：{quiz['explanation']}"
        
        return response
    
    def _handle_general_question(self, question: str) -> str:
        """
        处理一般性问题
        
        Args:
            question: 用户问题
        
        Returns:
            回答内容
        """
        keywords = self.llm_client.extract_keywords(question)
        
        context = ""
        for keyword in keywords[:2]:
            kg_context = self.kg_retriever.get_knowledge_context(keyword)
            if kg_context:
                context += kg_context + "\n\n"
        
        return self.llm_client.chat(question, context)
    
    def get_topic_overview(self, topic: str) -> str:
        """
        获取主题概览
        
        Args:
            topic: 主题名称
        
        Returns:
            主题详细概览
        """
        context = self.kg_retriever.get_knowledge_context(topic)
        related = self.kg_retriever.get_related_concepts(topic)
        prerequisites = self.kg_retriever.get_prerequisites(topic)
        
        if related:
            context += "\n\n相关概念：\n"
            for r in related[:5]:
                context += f"- {r['type']}: {r['name']}\n"
        
        if prerequisites:
            context += "\n\n前置知识：\n"
            for p in prerequisites[:5]:
                context += f"- {p['type']}: {p['name']}\n"
        
        prompt = f"请详细介绍Python中的'{topic}'，包括概念、用法、示例和注意事项。"
        return self.llm_client.chat(prompt, context)
    
    def start_interactive_session(self):
        """
        启动交互式会话
        
        提供命令行交互界面，支持多种命令
        """
        print("=" * 60)
        print("🐍 Python学习助手 - 基于知识图谱的智能问答系统")
        print("=" * 60)
        print("我可以帮助你：")
        print("  - 解答Python编程概念问题")
        print("  - 提供代码示例和解释")
        print("  - 推荐学习路径")
        print("  - 设计练习题目")
        print("  - 进行编程测验")
        print("\n输入 'quit' 或 'exit' 退出")
        print("输入 'clear' 清除对话历史")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见！祝你学习愉快！")
                    break
                
                if user_input.lower() == 'clear':
                    self.llm_client.clear_history()
                    print("✅ 对话历史已清除")
                    continue
                
                print("\n🤖 助手: ", end="")
                
                response = self.ask(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")


def main():
    """
    主函数
    
    创建并启动学习助手交互会话
    """
    assistant = PythonLearningAssistant()
    try:
        assistant.start_interactive_session()
    finally:
        assistant.close()


if __name__ == '__main__':
    main()
