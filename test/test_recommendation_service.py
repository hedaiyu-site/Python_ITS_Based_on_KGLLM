import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.recommendation_service import RecommendationService

async def test_recommendation_service():
    """测试RecommendationService功能"""
    print("开始测试RecommendationService...")
    
    # 创建RecommendationService实例
    recommendation_service = RecommendationService()
    
    # 测试1: 推荐学习内容
    print("\n1. 测试推荐学习内容:")
    user_id = 1
    content_type = "mixed"
    limit = 5
    
    try:
        recommendations = await recommendation_service.recommend_content(user_id, content_type, limit)
        print(f"推荐内容数量: {len(recommendations)}")
        for i, item in enumerate(recommendations, 1):
            print(f"{i}. {item['title']} (类型: {item.get('item_type', '未知')}, 相关度: {item.get('relevance_score', 0)})")
            if 'description' in item:
                print(f"   描述: {item['description']}")
    except Exception as e:
        print(f"测试1失败: {str(e)}")
    
    # 测试2: 推荐练习题
    print("\n2. 测试推荐练习题:")
    knowledge_node = "Python 函数"
    difficulty = "medium"
    limit = 3
    
    try:
        questions = await recommendation_service.recommend_questions(user_id, knowledge_node, difficulty, limit)
        print(f"推荐题目数量: {len(questions)}")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question['title']} (难度: {question['difficulty']})")
            if 'description' in question:
                print(f"   描述: {question['description']}")
    except Exception as e:
        print(f"测试2失败: {str(e)}")
    
    # 测试3: 更新用户偏好
    print("\n3. 测试更新用户偏好:")
    preferences = {
        "interests": ["Python", "数据科学", "机器学习", "人工智能"],
        "learning_style": "visual",
        "preferred_content_types": ["video", "course"],
        "skill_level": "intermediate"
    }
    
    try:
        result = await recommendation_service.update_preferences(user_id, preferences)
        print(f"更新结果: {result['message']}")
        print(f"用户ID: {result['user_id']}")
        print(f"更新后的偏好: {result['preferences']}")
    except Exception as e:
        print(f"测试3失败: {str(e)}")
    
    # 测试4: 获取推荐原因
    print("\n4. 测试获取推荐原因:")
    item_id = "item_123"
    
    try:
        reasons = await recommendation_service.get_recommendation_reasons(user_id, item_id)
        print(f"项目ID: {reasons['item_id']}")
        print("推荐原因:")
        for i, reason in enumerate(reasons['reasons'], 1):
            print(f"{i}. {reason}")
    except Exception as e:
        print(f"测试4失败: {str(e)}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(test_recommendation_service())