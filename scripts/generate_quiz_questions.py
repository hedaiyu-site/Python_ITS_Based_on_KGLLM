"""
批量生成测验题目脚本

从Neo4j知识图谱获取所有知识点，为每个知识点生成10道测验题目
难度分布: easy(4道), medium(3道), hard(3道)
"""

import sys
import os
import json
import time
import logging
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
import pymysql
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hedaiyu123"

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "123456"
MYSQL_DATABASE = "python_learning"

LLM_API_KEY = "sk-b40dc8abd15446e1b36464a10be57eee"
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_MODEL = "qwen-plus"

QUESTIONS_PER_POINT = 10
DIFFICULTY_DISTRIBUTION = ["easy", "easy", "easy", "easy", "medium", "medium", "medium", "hard", "hard", "hard"]


class QuestionGenerator:
    """题目生成器"""
    
    def __init__(self):
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.mysql_config = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "database": MYSQL_DATABASE,
            "charset": "utf8mb4"
        }
        self.llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    
    def close(self):
        """关闭连接"""
        self.neo4j_driver.close()
    
    def get_all_knowledge_points(self) -> List[Dict]:
        """从Neo4j获取所有知识点"""
        node_types = ["KnowledgePoint", "DataType", "Module", "Function", "Concept", "ControlStructure", "Operator", "Library", "Tool"]
        
        all_points = []
        with self.neo4j_driver.session(database="neo4j") as session:
            for node_type in node_types:
                result = session.run(f"MATCH (n:{node_type}) RETURN n.id as id, n.name as name")
                for r in result:
                    if r["id"] or r["name"]:
                        all_points.append({
                            "id": r["id"] or r["name"],
                            "name": r["name"],
                            "type": node_type
                        })
        
        return all_points
    
    def count_existing_questions(self, knowledge_point_id: str) -> int:
        """统计已有题目数量"""
        with pymysql.connect(**self.mysql_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM quiz_questions WHERE knowledge_point_id = %s",
                    (knowledge_point_id,)
                )
                return cursor.fetchone()[0]
    
    def count_questions_by_difficulty(self, knowledge_point_id: str) -> Dict[str, int]:
        """统计各难度题目数量"""
        with pymysql.connect(**self.mysql_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT difficulty, COUNT(*) FROM quiz_questions WHERE knowledge_point_id = %s GROUP BY difficulty",
                    (knowledge_point_id,)
                )
                result = {}
                for row in cursor.fetchall():
                    result[row[0]] = row[1]
                return result
    
    def generate_question(self, knowledge_point_name: str, difficulty: str, max_retries: int = 3) -> Dict:
        """使用LLM生成一道题目"""
        difficulty_desc = {
            "easy": "简单",
            "medium": "中等",
            "hard": "困难"
        }
        
        prompt = f"""你是一位Python编程教学专家。请为Python的"{knowledge_point_name}"知识点生成一道{difficulty_desc[difficulty]}难度的选择题。

要求：
1. 题目要有实际意义，考察对"{knowledge_point_name}"的理解和应用
2. 四个选项要有迷惑性，但只有一个正确答案
3. 提供详细的答案解析，解释为什么选这个答案
4. {"基础概念题，适合初学者" if difficulty == "easy" else "综合应用题，需要一定基础" if difficulty == "medium" else "深入理解题，需要扎实基础"}

请严格按照以下JSON格式返回，不要添加任何其他内容，不要使用markdown代码块：
{{"question":"题目内容","option_a":"选项A","option_b":"选项B","option_c":"选项C","option_d":"选项D","correct_answer":"A","explanation":"解析"}}"""

        for attempt in range(max_retries):
            try:
                response = self.llm_client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=500
                )
                
                content = response.choices[0].message.content.strip()
                
                content = content.replace("```json", "").replace("```", "").strip()
                
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    question_data = json.loads(json_str)
                    
                    question_data["correct_answer"] = question_data.get("correct_answer", "A").upper()
                    
                    required_fields = ["question", "option_a", "option_b", "option_c", "option_d", "correct_answer"]
                    for field in required_fields:
                        if field not in question_data:
                            raise ValueError(f"缺少字段: {field}")
                    
                    if question_data["correct_answer"] not in ["A", "B", "C", "D"]:
                        raise ValueError(f"无效的答案: {question_data['correct_answer']}")
                    
                    question_data["explanation"] = question_data.get("explanation", "")
                    
                    return question_data
                else:
                    raise ValueError("未找到JSON内容")
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            except Exception as e:
                logger.error(f"生成题目失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        return None
    
    def save_question(self, knowledge_point_id: str, knowledge_point_name: str, question_data: Dict, difficulty: str) -> bool:
        """保存题目到MySQL"""
        try:
            with pymysql.connect(**self.mysql_config) as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO quiz_questions 
                        (knowledge_point_id, knowledge_point_name, question, option_a, option_b, option_c, option_d, correct_answer, explanation, difficulty)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        knowledge_point_id,
                        knowledge_point_name,
                        question_data["question"],
                        question_data["option_a"],
                        question_data["option_b"],
                        question_data["option_c"],
                        question_data["option_d"],
                        question_data["correct_answer"],
                        question_data["explanation"],
                        difficulty
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"保存题目失败: {e}")
            return False
    
    def generate_for_knowledge_point(self, kp: Dict, target_count: int = QUESTIONS_PER_POINT) -> Dict:
        """为单个知识点生成题目"""
        kp_id = kp["id"]
        kp_name = kp["name"]
        
        existing_count = self.count_existing_questions(kp_id)
        existing_by_diff = self.count_questions_by_difficulty(kp_id)
        
        logger.info(f"知识点: {kp_name} (现有 {existing_count} 道题目)")
        
        if existing_count >= target_count:
            logger.info(f"  已有足够题目，跳过")
            return {"skipped": True, "existing": existing_count, "generated": 0}
        
        needed = target_count - existing_count
        generated = 0
        failed = 0
        
        for i in range(needed):
            difficulty = DIFFICULTY_DISTRIBUTION[(existing_count + i) % len(DIFFICULTY_DISTRIBUTION)]
            
            logger.info(f"  生成第 {existing_count + i + 1} 道题目 (难度: {difficulty})...")
            
            question_data = self.generate_question(kp_name, difficulty)
            
            if question_data:
                if self.save_question(kp_id, kp_name, question_data, difficulty):
                    generated += 1
                    logger.info(f"    成功: {question_data['question'][:50]}...")
                else:
                    failed += 1
            else:
                failed += 1
            
            time.sleep(0.5)
        
        return {"skipped": False, "existing": existing_count, "generated": generated, "failed": failed}
    
    def run(self, dry_run: bool = False):
        """执行批量生成"""
        logger.info("=" * 60)
        logger.info("开始批量生成测验题目")
        logger.info("=" * 60)
        
        knowledge_points = self.get_all_knowledge_points()
        logger.info(f"共获取 {len(knowledge_points)} 个知识点")
        
        if dry_run:
            logger.info("\n[DRY RUN] 以下知识点需要生成题目:")
            for kp in knowledge_points[:10]:
                count = self.count_existing_questions(kp["id"])
                if count < QUESTIONS_PER_POINT:
                    logger.info(f"  - {kp['name']}: 现有 {count} 道，需生成 {QUESTIONS_PER_POINT - count} 道")
            return
        
        total_generated = 0
        total_failed = 0
        total_skipped = 0
        
        for i, kp in enumerate(knowledge_points):
            logger.info(f"\n[{i+1}/{len(knowledge_points)}] 处理知识点: {kp['name']}")
            
            result = self.generate_for_knowledge_point(kp)
            
            if result["skipped"]:
                total_skipped += 1
            else:
                total_generated += result["generated"]
                total_failed += result["failed"]
        
        logger.info("\n" + "=" * 60)
        logger.info("生成完成!")
        logger.info(f"  总知识点数: {len(knowledge_points)}")
        logger.info(f"  跳过(已有足够题目): {total_skipped}")
        logger.info(f"  成功生成: {total_generated}")
        logger.info(f"  生成失败: {total_failed}")
        logger.info("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="批量生成测验题目")
    parser.add_argument("--dry-run", action="store_true", help="仅检查不生成")
    parser.add_argument("--limit", type=int, default=0, help="限制处理的知识点数量(0=不限制)")
    args = parser.parse_args()
    
    generator = QuestionGenerator()
    try:
        generator.run(dry_run=args.dry_run)
    finally:
        generator.close()


if __name__ == "__main__":
    main()
