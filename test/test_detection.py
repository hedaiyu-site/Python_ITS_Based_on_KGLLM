"""
用户水平检测算法测试脚本

测试用户水平检测算法的关键词匹配逻辑

测试内容:
- 初学者关键词检测
- 进阶用户关键词检测
- 边界情况处理
"""

import requests
import json


def test_detection():
    """
    测试用户水平检测算法
    
    使用关键词匹配判断用户水平
    """
    messages = [
        "Python初学者学习路径",
        "我有Python基础，想学习进阶内容",
        "Python高级教程学习路径",
        "零基础怎么学Python",
        "学过Python基础，想提升"
    ]
    
    for msg in messages:
        level = "all"
        msg_lower = msg.lower()
        
        beginner_keywords = ['初学者', '零基础', '入门', '新手', '刚开始', '基础', '小白', '从零开始']
        advanced_keywords = ['进阶', '高级', '深入', '高级教程', '提升', '进阶学习', '有基础', '学过', '掌握基础']
        
        for kw in advanced_keywords:
            if kw in msg_lower:
                level = "intermediate"
                break
        
        if level == "all":
            for kw in beginner_keywords:
                if kw in msg_lower:
                    level = "beginner"
                    break
        
        print(f"问题: {msg}")
        print(f"检测水平: {level}")
        print()


if __name__ == "__main__":
    test_detection()
