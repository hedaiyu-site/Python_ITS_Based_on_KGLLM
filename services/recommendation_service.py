from typing import List, Dict, Any
import uuid
from ai_services.llm_service import LLMService
from data.user_db import UserDB

class RecommendationService:
    """个性化推荐服务"""
    
    def __init__(self):
        """初始化推荐服务"""
        # 初始化大模型服务
        self.llm_service = LLMService()
        # 初始化数据库服务
        self.user_db = UserDB()
    
    async def recommend_content(self, user_id: int, content_type: str = "mixed", limit: int = 10) -> List[Dict[str, Any]]:
        """推荐学习内容"""
        # 获取用户偏好（实际项目中从数据库获取）
        # user_preferences = await self.user_db.get_user_preferences(user_id)
        user_preferences = {"interests": ["Python", "数据科学", "机器学习"], "learning_style": "visual"}
        
        # 使用大模型生成推荐内容
        prompt = f"请为用户推荐{limit}个{content_type}类型的学习内容，用户偏好：{user_preferences}\n"
        prompt += "每个推荐内容需要包含：\n"
        prompt += "1. 标题\n"
        prompt += "2. 类型（文章、视频、课程、书籍等）\n"
        prompt += "3. 简短描述\n"
        prompt += "4. 相关度评分（0-1）\n"
        prompt += "5. 推荐理由\n"
        
        response = await self.llm_service.generate(prompt)
        recommendations = []
        
        # 解析生成的推荐内容
        if response.get("text"):
            lines = response["text"].split('\n')
            current_item = {}
            for line in lines:
                line = line.strip()
                # 尝试不同的格式解析
                if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                    # 新的推荐项
                    if current_item and "title" in current_item:
                        recommendations.append(current_item)
                        if len(recommendations) >= limit:
                            break
                    current_item = {
                        "item_id": f"item_{uuid.uuid4().hex[:8]}",
                        "title": line[3:].strip()
                    }
                elif "标题：" in line:
                    current_item["title"] = line.split("标题：")[1].strip()
                elif "类型：" in line:
                    current_item["item_type"] = line.split("类型：")[1].strip()
                elif "描述：" in line:
                    current_item["description"] = line.split("描述：")[1].strip()
                elif "相关度：" in line:
                    try:
                        current_item["relevance_score"] = float(line.split("相关度：")[1].strip())
                    except:
                        current_item["relevance_score"] = 0.8
                elif "理由：" in line:
                    current_item["reason"] = line.split("理由：")[1].strip()
            
            # 添加最后一个推荐项
            if current_item and "title" in current_item and len(recommendations) < limit:
                recommendations.append(current_item)
        
        # 如果没有生成足够的推荐，添加默认推荐
        if len(recommendations) < limit:
            default_recommendations = [
                {
                    "item_id": f"item_{uuid.uuid4().hex[:8]}",
                    "item_type": "article",
                    "title": "Python 基础教程",
                    "description": "Python 入门级教程，适合初学者",
                    "relevance_score": 0.9
                },
                {
                    "item_id": f"item_{uuid.uuid4().hex[:8]}",
                    "item_type": "course",
                    "title": "数据科学入门",
                    "description": "数据科学基础课程，包含Python、统计学等内容",
                    "relevance_score": 0.85
                },
                {
                    "item_id": f"item_{uuid.uuid4().hex[:8]}",
                    "item_type": "video",
                    "title": "机器学习算法详解",
                    "description": "详细介绍常见机器学习算法的原理和应用",
                    "relevance_score": 0.8
                }
            ]
            
            for item in default_recommendations:
                if len(recommendations) < limit:
                    recommendations.append(item)
        
        return recommendations
    
    async def recommend_questions(self, user_id: int, knowledge_node: str, difficulty: str = "medium", limit: int = 5) -> List[Dict[str, Any]]:
        """推荐练习题"""
        # 使用大模型生成推荐题目
        prompt = f"请为{knowledge_node}知识点生成{limit}道{difficulty}难度的练习题\n"
        prompt += "每个题目需要包含：\n"
        prompt += "1. 题目名称\n"
        prompt += "2. 题目描述\n"
        prompt += "3. 难度级别\n"
        prompt += "4. 知识点\n"
        
        response = await self.llm_service.generate(prompt)
        questions = []
        
        # 解析生成的题目
        if response.get("text"):
            lines = response["text"].split('\n')
            current_question = {}
            for line in lines:
                line = line.strip()
                if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
                    # 新的题目
                    if current_question:
                        questions.append(current_question)
                        if len(questions) >= limit:
                            break
                    current_question = {
                        "question_id": f"q_{uuid.uuid4().hex[:8]}",
                        "title": line[3:].strip(),
                        "difficulty": difficulty,
                        "knowledge_node": knowledge_node
                    }
                elif "描述：" in line:
                    current_question["description"] = line.split("描述：")[1].strip()
            
            # 添加最后一个题目
            if current_question and len(questions) < limit:
                questions.append(current_question)
        
        # 如果没有生成足够的题目，添加默认题目
        if len(questions) < limit:
            for i in range(limit - len(questions)):
                questions.append({
                    "question_id": f"q_{uuid.uuid4().hex[:8]}",
                    "title": f"{knowledge_node}练习题{i+1}",
                    "description": f"关于{knowledge_node}的{difficulty}难度练习题",
                    "difficulty": difficulty,
                    "knowledge_node": knowledge_node
                })
        
        return questions
    
    async def update_preferences(self, user_id: int, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户偏好"""
        # 验证偏好数据
        if not isinstance(preferences, dict):
            preferences = {}
        
        # 更新偏好到数据库
        # 实际项目中需要实现相应的数据库方法
        # await self.user_db.update_user_preferences(user_id, preferences)
        
        return {
            "user_id": user_id,
            "preferences": preferences,
            "message": "偏好更新成功"
        }
    
    async def get_recommendation_reasons(self, user_id: int, item_id: str) -> Dict[str, Any]:
        """获取推荐原因"""
        # 获取用户信息和项目信息（实际项目中从数据库获取）
        # user_info = await self.user_db.get_user_info(user_id)
        # item_info = await self.user_db.get_item_info(item_id)
        user_info = {"interests": ["Python", "数据科学"], "learning_history": ["Python基础", "数据分析"]}
        item_info = {"title": "Python高级编程", "type": "course", "tags": ["Python", "高级编程"]}
        
        # 使用大模型生成推荐原因
        prompt = f"用户信息：{user_info}\n"
        prompt += f"推荐项目：{item_info}\n"
        prompt += "请生成3-5个推荐该项目给用户的具体原因，每个原因要具体、有说服力。"
        
        response = await self.llm_service.generate(prompt)
        reasons = []
        
        # 解析生成的原因
        if response.get("text"):
            lines = response["text"].split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    reasons.append(line)
        
        # 如果没有生成足够的原因，添加默认原因
        if not reasons:
            reasons = [
                "基于您的学习历史",
                "与您的兴趣相关",
                "有助于您的学习目标"
            ]
        
        return {
            "item_id": item_id,
            "reasons": reasons
        }