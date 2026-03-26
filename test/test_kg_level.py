"""
知识图谱服务学习路径测试脚本

测试知识图谱服务的学习路径获取功能

测试内容:
- 初学者学习路径
- 进阶用户学习路径
- 完整学习路径
"""

from app.services.kg_service import kg_service

print("测试不同水平的学习路径:\n")

print("=" * 60)
print("初学者路径:")
print("=" * 60)
print(kg_service.get_learning_path_by_level("beginner"))

print("\n" + "=" * 60)
print("进阶用户路径:")
print("=" * 60)
print(kg_service.get_learning_path_by_level("intermediate"))

print("\n" + "=" * 60)
print("完整路径:")
print("=" * 60)
print(kg_service.get_learning_path_by_level("all"))
