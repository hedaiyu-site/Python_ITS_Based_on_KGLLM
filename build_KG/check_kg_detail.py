from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hedaiyu123"

driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session(database="neo4j") as session:
    print("=" * 70)
    print("深入分析：当前数据库结构与代码定义的差异")
    print("=" * 70)
    
    print("\n【1. 检查所有实际存在的节点标签】")
    result = session.run("CALL db.labels() YIELD label RETURN label")
    all_labels = [r["label"] for r in result]
    print(f"  实际节点标签: {all_labels}")
    
    print("\n【2. 检查所有实际存在的关系类型】")
    result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
    all_rels = [r["relationshipType"] for r in result]
    print(f"  实际关系类型: {all_rels}")
    
    print("\n【3. 检查Course节点的属性】")
    result = session.run("MATCH (c:Course) RETURN c LIMIT 1")
    record = result.single()
    if record:
        print(f"  Course节点属性: {dict(record['c'])}")
    
    print("\n【4. 检查Chapter节点的属性】")
    result = session.run("MATCH (ch:Chapter) RETURN ch LIMIT 1")
    record = result.single()
    if record:
        print(f"  Chapter节点属性: {dict(record['ch'])}")
    
    print("\n【5. 检查一个完整的关系路径示例】")
    result = session.run("""
        MATCH (a)-[r]->(b)
        RETURN labels(a)[0] as from_type, type(r) as rel_type, labels(b)[0] as to_type, 
               a.name as from_name, b.name as to_name
        LIMIT 5
    """)
    for r in result:
        print(f"  ({r['from_type']}: {r['from_name'][:20]}) -[{r['rel_type']}]-> ({r['to_type']}: {r['to_name'][:20]})")
    
    print("\n【6. 代码定义 vs 实际数据库 对比】")
    print("-" * 70)
    
    code_node_types = ["Course", "Chapter", "Section", "KnowledgePoint", "DataType", 
                       "Module", "Function", "Concept", "ControlStructure", "Operator",
                       "Library", "Tool"]
    code_rel_types = ["HAS_CHAPTER", "HAS_SECTION", "HAS_KNOWLEDGE_POINT", 
                      "HAS_SUB_POINT", "RELATED_TO", "USED_FOR"]
    
    print("\n  节点类型对比:")
    print(f"    代码定义: {code_node_types}")
    print(f"    数据库实际: {all_labels}")
    
    missing_nodes = set(code_node_types) - set(all_labels)
    extra_nodes = set(all_labels) - set(code_node_types)
    if missing_nodes:
        print(f"    缺失的节点类型: {missing_nodes}")
    if extra_nodes:
        print(f"    多余的节点类型: {extra_nodes}")
    
    print("\n  关系类型对比:")
    print(f"    代码定义: {code_rel_types}")
    print(f"    数据库实际: {all_rels}")
    
    missing_rels = set(code_rel_types) - set(all_rels)
    extra_rels = set(all_rels) - set(code_rel_types)
    if missing_rels:
        print(f"    缺失的关系类型: {missing_rels}")
    if extra_rels:
        print(f"    多余的关系类型: {extra_rels}")
    
    print("\n" + "=" * 70)
    print("【结论】")
    if missing_nodes or missing_rels or extra_nodes or extra_rels:
        print("  数据库中的知识图谱结构与代码定义不一致!")
        print("  可能原因:")
        print("    1. 尚未运行 build_knowledge_graph.py 构建图谱")
        print("    2. 数据库中存在旧版本的知识图谱")
        print("  建议: 运行 build_knowledge_graph.py 重新构建")
    else:
        print("  数据库结构完全符合代码定义!")
    print("=" * 70)

driver.close()
