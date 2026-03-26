"""
知识图谱数据检查脚本

检查Neo4j数据库中的章节顺序数据

检查内容:
- 基础课程章节顺序
- 高级课程章节顺序
- order字段值验证
"""

from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_neo4j_password"
NEO4J_DATABASE = "neo4j"

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    print("=" * 60)
    print("基础课程章节顺序 (完整):")
    print("=" * 60)
    result = session.run("""
        MATCH (c:Course {id: 'course_basic'})-[r:HAS_CHAPTER]->(ch:Chapter)
        RETURN ch.name as name, r.order as order
        ORDER BY toInteger(r.order)
    """)
    for record in result:
        print(f"  [{record['order']}] {record['name']}")
    
    print("\n" + "=" * 60)
    print("高级课程章节顺序:")
    print("=" * 60)
    result = session.run("""
        MATCH (c:Course {id: 'course_advanced'})-[r:HAS_CHAPTER]->(ch:Chapter)
        RETURN ch.name as name, r.order as order
        ORDER BY toInteger(r.order)
    """)
    for record in result:
        print(f"  [{record['order']}] {record['name']}")

driver.close()
