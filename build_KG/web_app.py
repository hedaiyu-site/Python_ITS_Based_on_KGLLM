"""
Web应用模块(独立版本)

基于Streamlit框架的Python学习助手Web界面
提供可视化交互体验

主要功能:
- 聊天对话界面
- 快捷功能按钮
- 知识点搜索
- 知识图谱统计展示

依赖:
- streamlit: Web框架
- kg_retriever: 知识图谱检索器
- llm_client: 大模型客户端

作者: Python学习助手团队
版本: 1.0.0
"""

import streamlit as st
from kg_retriever import KnowledgeGraphRetriever
from llm_client import LLMClient
import time

st.set_page_config(
    page_title="Python学习助手",
    page_icon="🐍",
    layout="wide"
)


@st.cache_resource
def init_assistant():
    """
    初始化助手组件
    
    使用缓存避免重复初始化
    
    Returns:
        知识图谱检索器和大模型客户端实例
    """
    kg_retriever = KnowledgeGraphRetriever()
    llm_client = LLMClient()
    return kg_retriever, llm_client


kg_retriever, llm_client = init_assistant()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm_history" not in st.session_state:
    st.session_state.llm_history = []

st.title("🐍 Python学习助手")
st.caption("基于知识图谱 + 大模型的智能Python学习系统")

with st.sidebar:
    st.header("📚 功能导航")
    
    st.subheader("快捷功能")
    if st.button("📖 查看课程大纲"):
        st.session_state.messages.append({
            "role": "user", 
            "content": "请展示Python课程的完整大纲"
        })
    
    if st.button("🎯 生成练习题"):
        st.session_state.messages.append({
            "role": "user", 
            "content": "请给我出一道Python练习题"
        })
    
    if st.button("🛤️ 学习路径推荐"):
        st.session_state.messages.append({
            "role": "user", 
            "content": "作为Python初学者，请推荐学习路径"
        })
    
    st.divider()
    
    st.subheader("🔍 知识点搜索")
    search_topic = st.text_input("输入知识点关键词")
    if st.button("搜索") and search_topic:
        with st.spinner("正在搜索知识图谱..."):
            context = kg_retriever.get_knowledge_context(search_topic)
            related = kg_retriever.get_related_concepts(search_topic)
            
            if context:
                st.info(f"找到相关内容：\n{context[:500]}...")
            else:
                st.warning("未找到相关内容")
    
    st.divider()
    
    st.subheader("📊 知识图谱统计")
    if st.button("查看统计"):
        st.info("""
        **节点类型**: 12种
        - Course: 2个
        - Chapter: 18个
        - Section: 53个
        - KnowledgePoint: 37个
        - DataType: 13个
        - Module: 多个
        - 其他类型...
        
        **关系类型**: 5种
        - HAS_CHAPTER
        - HAS_SECTION
        - HAS_KNOWLEDGE_POINT
        - HAS_SUB_POINT
        - RELATED_TO
        """)
    
    st.divider()
    
    if st.button("🗑️ 清除对话"):
        st.session_state.messages = []
        st.session_state.llm_history = []
        llm_client.clear_history()
        st.rerun()


def classify_question(question: str) -> str:
    """
    分类问题类型
    
    Args:
        question: 用户问题
    
    Returns:
        问题类型
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
    return "general"


def get_response(question: str) -> str:
    """
    获取回答
    
    根据问题类型和知识图谱上下文生成回答
    
    Args:
        question: 用户问题
    
    Returns:
        回答内容
    """
    question_type = classify_question(question)
    keywords = llm_client.extract_keywords(question)
    
    context_parts = []
    for keyword in keywords[:3]:
        kg_context = kg_retriever.get_knowledge_context(keyword)
        if kg_context:
            context_parts.append(kg_context)
    
    if question_type == "path":
        basic_structure = kg_retriever.get_course_structure("basic")
        advanced_structure = kg_retriever.get_course_structure("advanced")
        
        context = "Python学习路径：\n\n"
        context += "【基础课程】\n"
        for ch in basic_structure['chapters']:
            context += f"  {ch['chapter']}\n"
        context += "\n【高级课程】\n"
        for ch in advanced_structure['chapters']:
            context += f"  {ch['chapter']}\n"
        
        context_parts.append(context)
    
    context = "\n\n".join(context_parts)
    
    return llm_client.chat(question, context)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("思考中..."):
            response = get_response(prompt)
        
        for chunk in response.split():
            full_response += chunk + " "
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.02)
        
        message_placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.divider()
st.caption("""
💡 **使用提示**：
- 询问概念：如"什么是列表推导式？"
- 请求代码：如"如何用Python读取文件？"
- 学习路径：如"Python初学者应该怎么学？"
- 练习题目：如"给我出一道函数的练习题"
""")
