from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_neo4j_password"

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session(database="neo4j") as session:
    print("=" * 70)
    print("知识图谱构建结果验证")
    print("=" * 70)
    
    print("\n【1. 核心节点类型统计 (代码定义的12种)】")
    code_node_types = ["Course", "Chapter", "Section", "KnowledgePoint", "DataType", 
                       "Module", "Function", "Concept", "ControlStructure", "Operator",
                       "Library", "Tool"]
    
    total_nodes = 0
    found_types = []
    for nt in code_node_types:
        result = session.run(f"MATCH (n:{nt}) RETURN count(n) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"  {nt}: {count} 个节点")
            total_nodes += count
            found_types.append(nt)
    
    print(f"\n  总节点数: {total_nodes}")
    print(f"  节点类型数: {len(found_types)}/12 种")
    
    print("\n【2. 核心关系类型统计 (代码定义的6种)】")
    code_rel_types = ["HAS_CHAPTER", "HAS_SECTION", "HAS_KNOWLEDGE_POINT", 
                      "HAS_SUB_POINT", "RELATED_TO", "USED_FOR"]
    
    total_rels = 0
    found_rels = []
    for rt in code_rel_types:
        result = session.run(f"MATCH ()-[r:{rt}]->() RETURN count(r) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"  {rt}: {count} 条关系")
            total_rels += count
            found_rels.append(rt)
    
    print(f"\n  总关系数: {total_rels}")
    print(f"  关系类型数: {len(found_rels)}/6 种")
    
    print("\n【3. 课程结构验证】")
    result = session.run("MATCH (c:Course) RETURN c.name as name, c.id as id ORDER BY c.id")
    for r in result:
        print(f"  课程: {r['name']} (id: {r['id']})")
    
    print("\n【4. 知识层级路径示例】")
    result = session.run("""
        MATCH path = (c:Course)-[:HAS_CHAPTER]->(ch:Chapter)-[:HAS_SECTION]->(s:Section)-[:HAS_KNOWLEDGE_POINT]->(kp)
        RETURN c.name as course, ch.name as chapter, s.name as section, kp.name as kp_name, labels(kp)[0] as kp_type
        LIMIT 5
    """)
    for r in result:
        print(f"  {r['course']}")
        print(f"    └─ {r['chapter']}")
        print(f"        └─ {r['section']}")
        print(f"            └─ [{r['kp_type']}] {r['kp_name']}")
    
    print("\n【5. DataType节点示例】")
    result = session.run("MATCH (dt:DataType) RETURN dt.name as name LIMIT 8")
    names = [r["name"] for r in result]
    print(f"  {names}")
    
    print("\n【6. Module节点示例】")
    result = session.run("MATCH (m:Module) RETURN m.name as name LIMIT 8")
    names = [r["name"] for r in result]
    print(f"  {names}")
    
    print("\n【7. Concept节点示例】")
    result = session.run("MATCH (c:Concept) RETURN c.name as name LIMIT 8")
    names = [r["name"] for r in result]
    print(f"  {names}")
    
    print("\n【8. RELATED_TO关系验证】")
    result = session.run("""
        MATCH (a)-[r:RELATED_TO]->(b)
        RETURN a.name as from_name, labels(a)[0] as from_type, b.name as to_name, labels(b)[0] as to_type
    """)
    for r in result:
        print(f"  ({r['from_type']}: {r['from_name']}) -[RELATED_TO]-> ({r['to_type']}: {r['to_name']})")
    
    print("\n" + "=" * 70)
    print("【验证结果】")
    print(f"  节点类型: {len(found_types)}/12 种 {'OK' if len(found_types) >= 8 else 'X'}")
    print(f"  关系类型: {len(found_rels)}/6 种 {'OK' if len(found_rels) >= 5 else 'X'}")
    print(f"  总节点数: {total_nodes}")
    print(f"  总关系数: {total_rels}")
    
    if len(found_types) == 12 and len(found_rels) >= 5:
        print("\n  知识图谱构建成功，结构符合代码定义!")
    print("=" * 70)

driver.close()
