from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_neo4j_password"

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session(database="neo4j") as session:
    print("=" * 60)
    print("Neo4j 知识图谱构建结果检查")
    print("=" * 60)
    
    print("\n【节点类型统计】")
    node_types = ["Course", "Chapter", "Section", "KnowledgePoint", "DataType", 
                  "Module", "Function", "Concept", "ControlStructure", "Operator",
                  "Library", "Tool"]
    
    total_nodes = 0
    actual_types = []
    for nt in node_types:
        result = session.run(f"MATCH (n:{nt}) RETURN count(n) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"  {nt}: {count} 个节点")
            total_nodes += count
            actual_types.append(nt)
    
    print(f"\n  总节点数: {total_nodes}")
    print(f"  节点类型数: {len(actual_types)} 种")
    
    print("\n【关系统计】")
    result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
    all_rel_types = [r["relationshipType"] for r in result]
    
    total_relations = 0
    for rt in all_rel_types:
        result = session.run(f"MATCH ()-[r:{rt}]->() RETURN count(r) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"  {rt}: {count} 条关系")
            total_relations += count
    
    print(f"\n  总关系数: {total_relations}")
    
    print("\n【课程结构】")
    result = session.run("MATCH (c:Course) RETURN c.name as name, c.id as id")
    for r in result:
        print(f"  课程: {r['name']} (id: {r['id']})")
    
    print("\n【章节示例 (前5个)】")
    result = session.run("MATCH (ch:Chapter) RETURN ch.name as name LIMIT 5")
    for r in result:
        print(f"  章节: {r['name']}")
    
    print("\n【数据类型节点】")
    result = session.run("MATCH (dt:DataType) RETURN dt.name as name")
    for r in result:
        print(f"  - {r['name']}")
    
    print("\n【模块节点】")
    result = session.run("MATCH (m:Module) RETURN m.name as name")
    for r in result:
        print(f"  - {r['name']}")
    
    print("\n【概念节点 (前10个)】")
    result = session.run("MATCH (c:Concept) RETURN c.name as name LIMIT 10")
    for r in result:
        print(f"  - {r['name']}")
    
    print("\n【示例：查看一个完整的知识路径】")
    result = session.run("""
        MATCH path = (c:Course)-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_SECTION]->(s:Section)-[:HAS_KNOWLEDGE_POINT]->(kp)
        RETURN c.name as course, ch.name as chapter, s.name as section, kp.name as knowledge_point
        LIMIT 3
    """)
    for r in result:
        print(f"  {r['course']} > {r['chapter']} > {r['section']} > {r['knowledge_point']}")
    
    print("\n" + "=" * 60)
    print("【要求检查结果】")
    if len(actual_types) >= 8:
        print(f"  OK 节点类型: {len(actual_types)}种 (满足>=8种要求)")
    else:
        print(f"  X 节点类型: {len(actual_types)}种 (不满足>=8种要求)")
    
    if len(all_rel_types) >= 5:
        print(f"  OK 关系类型: {len(all_rel_types)}种 (满足>=5种要求)")
    else:
        print(f"  X 关系类型: {len(all_rel_types)}种 (不满足>=5种要求)")
    print("=" * 60)

driver.close()
