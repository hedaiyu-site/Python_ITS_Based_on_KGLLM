from neo4j import GraphDatabase

class Neo4jVerifier:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_node_count(self):
        """获取节点总数"""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            return result.single()['count']
    
    def get_relationship_count(self):
        """获取关系总数"""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()['count']
    
    def get_sample_nodes(self, limit=10):
        """获取样本节点"""
        with self.driver.session() as session:
            result = session.run(f"MATCH (n) RETURN n.name as name, n.source as source LIMIT {limit}")
            return [dict(record) for record in result]
    
    def get_sample_relationships(self, limit=10):
        """获取样本关系"""
        with self.driver.session() as session:
            result = session.run(f"MATCH (a)-[r]->(b) RETURN a.name as from, type(r) as type, b.name as to LIMIT {limit}")
            return [dict(record) for record in result]

if __name__ == "__main__":
    # 连接信息
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "hedaiyu123"
    
    verifier = Neo4jVerifier(uri, user, password)
    
    try:
        print("=== 知识图谱验证结果 ===")
        
        # 节点和关系数量
        node_count = verifier.get_node_count()
        rel_count = verifier.get_relationship_count()
        print(f"节点总数: {node_count}")
        print(f"关系总数: {rel_count}")
        
        # 样本节点
        print("\n样本节点:")
        sample_nodes = verifier.get_sample_nodes()
        for node in sample_nodes:
            print(f"  {node['name']} (来自: {node['source']})")
        
        # 样本关系
        print("\n样本关系:")
        sample_rels = verifier.get_sample_relationships()
        for rel in sample_rels:
            print(f"  {rel['from']} -[{rel['type']}]-> {rel['to']}")
        
        print("\n=== 验证完成 ===")
        print("知识图谱构建成功！您可以通过neo4j浏览器访问 http://localhost:7474 查看完整的知识图谱。")
        
    finally:
        verifier.close()
