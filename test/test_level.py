"""
用户水平检测测试脚本

测试不同用户水平的学习路径推荐功能

测试场景:
- 初学者查询
- 进阶用户查询
- 高级教程请求

验证:
- 用户水平检测是否正确
- 学习路径推荐是否匹配用户水平
"""

import requests
import json
import time


def test_query(message, description):
    """
    执行单个测试查询
    
    Args:
        message: 测试消息
        description: 测试描述
    """
    url = "http://localhost:8001/chat/stream"
    data = {"message": message}
    
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"问题: {message}")
    print("="*60)
    
    start_time = time.time()
    first_chunk_time = None
    
    try:
        response = requests.post(url, json=data, stream=True, timeout=30)
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    content = line[6:]
                    if content == '[DONE]':
                        break
                    try:
                        json_data = json.loads(content)
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            print(f"首字响应: {(first_chunk_time - start_time)*1000:.0f}ms\n")
                        full_response += json_data['content']
                    except:
                        pass
        
        print(full_response)
        print(f"\n总时间: {(time.time() - start_time)*1000:.0f}ms")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("测试不同用户水平的学习路径推荐")
    print("="*60)
    
    test_query("我是Python初学者，想学习Python", "初学者")
    test_query("我有Python基础，想学习进阶内容", "进阶用户")
    test_query("我想学习Python高级教程", "高级教程请求")
