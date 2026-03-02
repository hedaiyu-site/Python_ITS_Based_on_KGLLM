import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.learning_path_service import LearningPathService

async def test_learning_path_service():
    """测试LearningPathService功能"""
    print("开始测试LearningPathService...")
    
    # 创建LearningPathService实例
    learning_path_service = LearningPathService()
    
    # 测试1: 生成学习路径
    print("\n1. 测试生成学习路径:")
    user_id = 1
    target_skill = "Python 数据科学"
    
    try:
        path = await learning_path_service.generate_path(user_id, target_skill)
        print(f"路径ID: {path['path_id']}")
        print(f"目标技能: {path['target_skill']}")
        print(f"生成时间: {path['created_at']}")
        print(f"学习节点数量: {len(path['nodes'])}")
        print(f"学习节点: {path['nodes']}")
        print(f"初始进度: {path['progress']}")
    except Exception as e:
        print(f"测试1失败: {str(e)}")
    
    # 测试2: 更新学习进度
    print("\n2. 测试更新学习进度:")
    try:
        # 使用测试1生成的路径ID
        path_id = path['path_id']
        node_id = path['nodes'][0] if path['nodes'] else "基础概念"
        
        update_result = await learning_path_service.update_progress(user_id, node_id, 0.8, True)
        print(f"更新结果: {update_result}")
    except Exception as e:
        print(f"测试2失败: {str(e)}")
    
    # 测试3: 获取学习进度
    print("\n3. 测试获取学习进度:")
    try:
        progress = await learning_path_service.get_progress(user_id, path_id)
        print(f"路径ID: {progress['path_id']}")
        print(f"学习进度: {progress['progress']}")
        print(f"整体完成度: {progress['overall_completion'] * 100}%")
    except Exception as e:
        print(f"测试3失败: {str(e)}")
    
    # 测试4: 优化学习路径
    print("\n4. 测试优化学习路径:")
    try:
        optimized_path = await learning_path_service.optimize_path(user_id, path_id)
        print(f"路径ID: {optimized_path['path_id']}")
        print(f"优化后的节点数量: {len(optimized_path['nodes'])}")
        print(f"优化后的节点: {optimized_path['nodes']}")
        print(f"优化状态: {optimized_path['optimized']}")
    except Exception as e:
        print(f"测试4失败: {str(e)}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(test_learning_path_service())