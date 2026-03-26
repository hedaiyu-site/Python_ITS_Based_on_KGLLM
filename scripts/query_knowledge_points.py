"""
查询Neo4j知识图谱中的所有知识点
"""

from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_neo4j_password"

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session(database="neo4j") as session:
    node_types = ["KnowledgePoint", "DataType", "Module", "Function", "Concept", "ControlStructure", "Operator", "Library", "Tool"]
    
    total = 0
    all_points = []
    
    for node_type in node_types:
        result = session.run(f"MATCH (n:{node_type}) RETURN n.id as id, n.name as name")
        for r in result:
            if r["id"] or r["name"]:
                all_points.append({
                    "id": r["id"] or r["name"],
                    "name": r["name"],
                    "type": node_type
                })
                total += 1
    
    print(f"知识点总数: {total}")
    print(f"\n各类型数量:")
    for node_type in node_types:
        result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"  {node_type}: {count}")
    
    print(f"\n前20个知识点示例:")
    for i, p in enumerate(all_points[:20]):
        print(f"  {i+1}. [{p['type']}] {p['name']} (id: {p['id']})")

driver.close()
