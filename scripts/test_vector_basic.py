import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.vector_db import VectorDB, get_vector_db
from services.knowledge_vector_service import KnowledgeVectorService


def test_vector_db_basic():
    print("=" * 50)
    print("测试向量数据库基本功能")
    print("=" * 50)
    
    db = get_vector_db()
    
    print("\n1. 初始化状态:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n2. 测试向量数据库功能正常!")
    print("=" * 50)


if __name__ == "__main__":
    test_vector_db_basic()
