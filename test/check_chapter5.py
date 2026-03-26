"""
章节顺序调试脚本

检查Neo4j数据库中章节的order值和ID

调试内容:
- 所有章节的order值
- 章节ID和名称对应关系
- 查找特定章节
"""

from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hedaiyu123"
NEO4J_DATABASE = "neo4j"

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    print("检查所有章节和order值:")
    result = session.run("""
        MATCH (c:Course {id: 'course_basic'})-[r:HAS_CHAPTER]->(ch:Chapter)
        RETURN ch.name as name, ch.id as id, r.order as order
        ORDER BY r.order
    """)
    for record in result:
        print(f"  order={record['order']}, id={record['id']}, name={record['name']}")
    
    print("\n检查是否有'函数'相关的章节:")
    result = session.run("""
        MATCH (ch:Chapter)
        WHERE ch.name CONTAINS '函数' OR ch.name CONTAINS '五'
        RETURN ch.name as name, ch.id as id
    """)
    for record in result:
        print(f"  id={record['id']}, name={record['name']}")

driver.close()
