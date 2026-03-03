from neo4j import GraphDatabase

class Neo4jDetailedVerifier:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_node_type_stats(self):
        """获取各类型节点数量"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WITH labels(n) as labels, count(n) as count
                RETURN labels[0] as type, count
                ORDER BY count DESC
            """)
            return [(record['type'], record['count']) for record in result]
    
    def get_relationship_type_stats(self):
        """获取各类型关系数量"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH ()-[r]->()
                WITH type(r) as type, count(r) as count
                RETURN type, count
                ORDER BY count DESC
            """)
            return [(record['type'], record['count']) for record in result]
    
    def get_total_counts(self):
        """获取总数"""
        with self.driver.session() as session:
            node_result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = node_result.single()['count']
            
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = rel_result.single()['count']
            
            return node_count, rel_count

if __name__ == "__main__":
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "hedaiyu123"
    
    verifier = Neo4jDetailedVerifier(uri, user, password)
    
    try:
        print("=" * 60)
        print("知识图谱详细统计报告")
        print("=" * 60)
        
        node_count, rel_count = verifier.get_total_counts()
        print(f"\n【总体统计】")
        print(f"  节点总数: {node_count}")
        print(f"  关系总数: {rel_count}")
        
        print(f"\n【节点类型统计】")
        node_types = verifier.get_node_type_stats()
        for type_name, count in node_types:
            print(f"  {type_name}: {count}")
        print(f"  节点类型总数: {len(node_types)}")
        
        print(f"\n【关系类型统计】")
        rel_types = verifier.get_relationship_type_stats()
        for type_name, count in rel_types:
            print(f"  {type_name}: {count}")
        print(f"  关系类型总数: {len(rel_types)}")
        
        print("\n" + "=" * 60)
        print("【达标情况检查】")
        print("=" * 60)
        
        node_type_count = len(node_types)
        rel_type_count = len(rel_types)
        
        print(f"  节点类型数量: {node_type_count} {'✅ 达标' if node_type_count >= 8 else '❌ 未达标 (要求≥8类)'}")
        print(f"  关系类型数量: {rel_type_count} {'✅ 达标' if rel_type_count >= 5 else '❌ 未达标 (要求≥5种)'}")
        
    finally:
        verifier.close()
