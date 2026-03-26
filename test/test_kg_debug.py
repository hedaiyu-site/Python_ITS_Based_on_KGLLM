"""
知识图谱服务调试测试脚本

测试知识图谱服务的各项功能

测试内容:
- 用户水平检测
- 进阶学习路径获取
- 知识点搜索
"""

from app.services.kg_service import kg_service

print("测试知识图谱服务:")
print("="*60)

print("\n1. 检测用户水平:")
test_messages = [
    "我有Python基础，想学习进阶内容",
    "我想学习Python高级教程",
    "我是Python初学者"
]

for msg in test_messages:
    beginner_keywords = ['初学者', '零基础', '入门', '新手', '刚开始', '基础', '小白', '从零开始']
    advanced_keywords = ['进阶', '高级', '深入', '高级教程', '提升', '进阶学习', '有基础', '学过', '掌握基础']
    
    level = "all"
    for kw in advanced_keywords:
        if kw in msg:
            level = "intermediate"
            break
    
    if level == "all":
        for kw in beginner_keywords:
            if kw in msg:
                level = "beginner"
                break
    
    print(f"  '{msg}' -> {level}")

print("\n2. 获取进阶学习路径:")
path = kg_service.get_learning_path_by_level("intermediate")
print(path)

print("\n3. 搜索'高级'相关内容:")
context = kg_service.search_context("高级")
print(context if context else "无结果")

print("\n4. 搜索'进阶'相关内容:")
context = kg_service.search_context("进阶")
print(context if context else "无结果")
