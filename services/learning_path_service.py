from typing import List, Dict, Any
import uuid
import time
from ai_services.llm_service import LLMService
from data.user_db import UserDB

class LearningPathService:
    """学习路径规划服务"""
    
    def __init__(self):
        """初始化学习路径服务"""
        # 初始化大模型服务
        self.llm_service = LLMService()
        # 初始化数据库服务
        self.user_db = UserDB()
    
    async def generate_path(self, user_id: int, target_skill: str) -> Dict[str, Any]:
        """生成个性化学习路径"""
        # 生成唯一路径ID
        path_id = f"path_{uuid.uuid4().hex[:8]}"
        created_at = time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # 使用大模型生成学习路径
        prompt = f"请为目标技能 '{target_skill}' 生成一个详细的学习路径，包括：\n"
        prompt += "1. 学习阶段划分（如基础、进阶、高级）\n"
        prompt += "2. 每个阶段的核心知识点\n"
        prompt += "3. 推荐的学习资源（如书籍、课程、文档）\n"
        prompt += "4. 学习顺序和依赖关系\n"
        prompt += "5. 每个阶段的学习时间估计\n"
        
        response = await self.llm_service.generate(prompt)
        path_content = response.get("text", "")
        
        # 解析生成的路径内容，提取节点
        # 这里简化处理，实际项目中需要更复杂的解析逻辑
        nodes = []
        if path_content:
            # 简单分割生成节点
            lines = path_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    nodes.append(line[:100])  # 限制节点长度
        
        if not nodes:
            # 默认节点
            nodes = [
                f"{target_skill} 基础概念",
                f"{target_skill} 核心技术",
                f"{target_skill} 实践应用",
                f"{target_skill} 高级主题"
            ]
        
        # 保存学习路径到数据库
        # 实际项目中需要实现相应的数据库方法
        # await self.user_db.save_learning_path(path_id, user_id, target_skill, nodes)
        
        return {
            "path_id": path_id,
            "user_id": user_id,
            "target_skill": target_skill,
            "nodes": nodes,
            "progress": {node: 0.0 for node in nodes},
            "created_at": created_at,
            "path_content": path_content
        }
    
    async def update_progress(self, user_id: int, node_id: str, mastery_level: float, completed: bool) -> Dict[str, Any]:
        """更新学习进度"""
        # 验证输入
        if mastery_level < 0 or mastery_level > 1:
            mastery_level = max(0, min(1, mastery_level))
        
        # 更新进度到数据库
        # 实际项目中需要实现相应的数据库方法
        # await self.user_db.update_learning_progress(user_id, node_id, mastery_level, completed)
        
        return {
            "user_id": user_id,
            "node_id": node_id,
            "mastery_level": mastery_level,
            "completed": completed
        }
    
    async def get_progress(self, user_id: int, path_id: str) -> Dict[str, Any]:
        """获取学习进度"""
        # 从数据库获取进度
        # 实际项目中需要实现相应的数据库方法
        # progress = await self.user_db.get_learning_progress(user_id, path_id)
        
        # 模拟进度数据
        progress = {
            "基础概念": 0.8,
            "核心技术": 0.5,
            "实践应用": 0.2,
            "高级主题": 0.0
        }
        
        # 计算整体完成度
        if progress:
            overall_completion = sum(progress.values()) / len(progress)
        else:
            overall_completion = 0.0
        
        return {
            "path_id": path_id,
            "progress": progress,
            "overall_completion": round(overall_completion, 2)
        }
    
    async def optimize_path(self, user_id: int, path_id: str) -> Dict[str, Any]:
        """优化学习路径"""
        # 获取当前路径信息
        current_path = await self.get_progress(user_id, path_id)
        current_progress = current_path.get("progress", {})
        
        # 使用大模型优化路径
        prompt = f"请根据当前学习进度优化学习路径，当前进度：\n"
        for node, progress in current_progress.items():
            prompt += f"- {node}: {progress * 100}%\n"
        prompt += "\n请基于以下原则优化：\n"
        prompt += "1. 优先推荐当前进度较低的节点\n"
        prompt += "2. 考虑学习内容的依赖关系\n"
        prompt += "3. 提供更详细的学习建议\n"
        prompt += "4. 调整学习顺序以提高效率\n"
        
        response = await self.llm_service.generate(prompt)
        optimized_content = response.get("text", "")
        
        # 解析优化后的路径
        optimized_nodes = list(current_progress.keys())
        if optimized_content:
            # 简单处理，实际项目中需要更复杂的解析
            lines = optimized_content.split('\n')
            new_nodes = []
            for line in lines:
                line = line.strip()
                if line and ('-' in line or '#' in line):
                    new_nodes.append(line[:100])
            if new_nodes:
                optimized_nodes = new_nodes
        
        return {
            "path_id": path_id,
            "nodes": optimized_nodes,
            "optimized": True,
            "optimization_content": optimized_content
        }