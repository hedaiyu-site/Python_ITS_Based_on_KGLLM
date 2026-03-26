"""
测验业务服务

提供测验题目生成、答题、评分等业务逻辑
"""

from typing import List, Dict, Any, Optional
import logging
import json

from app.repositories.mysql.quiz_repository import QuizRepository
from app.repositories.mysql.learning_path_repository import LearningPathRepository
from app.ai.llm_service import LLMService

logger = logging.getLogger(__name__)


class QuizService:
    """测验业务服务"""
    
    def __init__(
        self,
        quiz_repository: QuizRepository,
        learning_path_repository: LearningPathRepository,
        llm_service: LLMService
    ):
        self._quiz_repo = quiz_repository
        self._learning_path_repo = learning_path_repository
        self._llm = llm_service
    
    def generate_and_save_questions(
        self, 
        knowledge_point_id: str, 
        knowledge_point_name: str,
        count: int = 10
    ) -> Dict[str, Any]:
        """
        为知识点生成并保存测验题目
        
        使用大模型生成题目，然后保存到数据库
        """
        existing_count = self._quiz_repo.count_questions_by_knowledge_point(knowledge_point_id)
        
        if existing_count >= count:
            logger.info(f"知识点 {knowledge_point_name} 已有 {existing_count} 道题目，跳过生成")
            return {
                "success": True,
                "message": "题目已存在",
                "existing_count": existing_count,
                "generated_count": 0
            }
        
        generated_count = 0
        difficulties = ["easy", "medium", "hard"]
        
        for i in range(count - existing_count):
            difficulty = difficulties[i % 3]
            
            prompt = f"""为Python的"{knowledge_point_name}"生成一道{difficulty}难度的选择题。

要求：
1. 题目要有实际意义，考察对{knowledge_point_name}的理解
2. 四个选项要有迷惑性
3. 提供详细的答案解析

请严格按照以下JSON格式返回：
{{
    "question": "题目内容",
    "option_a": "选项A的内容",
    "option_b": "选项B的内容",
    "option_c": "选项C的内容",
    "option_d": "选项D的内容",
    "correct_answer": "正确答案字母(A/B/C/D)",
    "explanation": "答案解析"
}}

只返回JSON，不要其他内容。"""

            try:
                response = self._llm.chat(prompt, temperature=0.8)
                
                question_data = json.loads(response.strip())
                
                self._quiz_repo.create_question(
                    knowledge_point_id=knowledge_point_id,
                    knowledge_point_name=knowledge_point_name,
                    question=question_data['question'],
                    option_a=question_data['option_a'],
                    option_b=question_data['option_b'],
                    option_c=question_data['option_c'],
                    option_d=question_data['option_d'],
                    correct_answer=question_data['correct_answer'].upper(),
                    explanation=question_data.get('explanation', ''),
                    difficulty=difficulty
                )
                
                generated_count += 1
                logger.info(f"生成题目 {generated_count}/{count - existing_count}: {knowledge_point_name}")
                
            except Exception as e:
                logger.error(f"生成题目失败: {e}")
                continue
        
        return {
            "success": True,
            "message": f"成功生成 {generated_count} 道题目",
            "existing_count": existing_count,
            "generated_count": generated_count
        }
    
    def get_quiz_questions(
        self, 
        knowledge_point_id: str, 
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取知识点的测验题目
        
        如果题目不足10道，自动生成补充
        """
        questions = self._quiz_repo.get_questions_by_knowledge_point(knowledge_point_id, count)
        
        return [
            {
                "id": q['id'],
                "question": q['question'],
                "options": [
                    f"A. {q['option_a']}",
                    f"B. {q['option_b']}",
                    f"C. {q['option_c']}",
                    f"D. {q['option_d']}"
                ],
                "answer": q['correct_answer']
            }
            for q in questions
        ]
    
    def submit_answer(
        self,
        user_id: int,
        knowledge_point_id: str,
        knowledge_point_name: str,
        question_id: int,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        提交答案并评分
        
        返回答题结果，并更新知识点掌握程度
        """
        question = self._quiz_repo.get_question_by_id(question_id)
        if not question:
            return {
                "success": False,
                "message": "题目不存在"
            }
        
        is_correct = user_answer.upper() == question['correct_answer'].upper()
        
        self._quiz_repo.save_quiz_record(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            question_id=question_id,
            user_answer=user_answer.upper(),
            is_correct=is_correct
        )
        
        self._learning_path_repo.increment_quiz_stats(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id,
            is_correct=is_correct
        )
        
        progress = self._learning_path_repo.get_knowledge_progress(user_id, knowledge_point_id)
        if progress:
            quiz_count = progress.get('quiz_count', 0) + 1
            correct_count = progress.get('correct_count', 0) + (1 if is_correct else 0)
            quiz_score = (correct_count / quiz_count) * 100
            
            self._learning_path_repo.update_knowledge_progress(
                user_id=user_id,
                knowledge_point_id=knowledge_point_id,
                knowledge_point_name=knowledge_point_name,
                status="mastered" if quiz_score >= 80 else ("learning" if quiz_score >= 50 else "reviewing"),
                mastery_level=int(quiz_score),
                quiz_score=quiz_score
            )
        
        return {
            "success": True,
            "is_correct": is_correct,
            "correct_answer": question['correct_answer'],
            "explanation": question.get('explanation', ''),
            "your_answer": user_answer.upper()
        }
    
    def get_quiz_statistics(self, user_id: int, knowledge_point_id: str) -> Dict[str, Any]:
        """获取知识点测验统计"""
        progress = self._learning_path_repo.get_knowledge_progress(user_id, knowledge_point_id)
        
        if not progress:
            return {
                "success": False,
                "message": "知识点进度不存在"
            }
        
        history = self._quiz_repo.get_user_quiz_history(user_id, knowledge_point_id, limit=10)
        
        quiz_count = progress.get('quiz_count', 0) or 0
        correct_count = progress.get('correct_count', 0) or 0
        accuracy = round((correct_count / quiz_count) * 100, 2) if quiz_count > 0 else 0.0
        
        return {
            "success": True,
            "quiz_count": quiz_count,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "mastery_level": progress.get('mastery_level', 0),
            "recent_history": history
        }
    
    def get_quiz_knowledge_points(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户可测验的知识点列表
        
        直接从quiz_questions表获取有题目的知识点，并结合用户学习进度
        """
        kp_with_questions = self._quiz_repo.get_all_knowledge_points_with_questions()
        
        all_progress = self._learning_path_repo.get_all_knowledge_progress(user_id)
        progress_map = {p['knowledge_point_id']: p for p in all_progress}
        
        result = []
        for kp in kp_with_questions:
            kp_id = kp['knowledge_point_id']
            kp_name = kp['knowledge_point_name']
            question_count = kp['question_count']
            
            progress = None
            for pid, p in progress_map.items():
                if kp_id.startswith(pid) or pid in kp_id:
                    progress = p
                    break
            
            result.append({
                "id": kp_id,
                "name": kp_name,
                "question_count": question_count,
                "mastery_level": progress.get('mastery_level', 0) if progress else 0,
                "status": progress.get('status', 'not_started') if progress else 'not_started'
            })
        
        return result
