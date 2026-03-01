import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chat_service import ChatService

async def test_chat_service():
    """测试ChatService功能"""
    print("开始测试ChatService...")
    
    # 创建ChatService实例
    chat_service = ChatService()
    
    # 测试1: 发送问题
    print("\n1. 测试发送问题:")
    user_id = 1
    question = "Python"
    
    try:
        response = await chat_service.ask_question(user_id, question, [])
        print(f"问题: {question}")
        print(f"回答: {response['answer']}")
        print(f"响应ID: {response['response_id']}")
        print(f"响应时间: {response['response_time']}秒")
    except Exception as e:
        print(f"测试1失败: {str(e)}")
    
    # 测试2: 获取对话历史
    print("\n2. 测试获取对话历史:")
    try:
        history = await chat_service.get_history(user_id)
        print(f"历史记录总数: {history['total']}")
        print(f"历史记录: {history['history']}")
    except Exception as e:
        print(f"测试2失败: {str(e)}")
    
    # 测试3: 提交反馈
    print("\n3. 测试提交反馈:")
    try:
        # 使用测试1的响应ID
        feedback = await chat_service.submit_feedback(response['response_id'], 5, "回答很详细，非常有帮助")
        print(f"反馈结果: {feedback}")
    except Exception as e:
        print(f"测试3失败: {str(e)}")
    
    # 测试4: 清空对话历史
    print("\n4. 测试清空对话历史:")
    try:
        result = await chat_service.clear_history(user_id)
        print(f"清空结果: {result}")
        
        # 验证是否清空
        history = await chat_service.get_history(user_id)
        print(f"清空后历史记录总数: {history['total']}")
    except Exception as e:
        print(f"测试4失败: {str(e)}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(test_chat_service())