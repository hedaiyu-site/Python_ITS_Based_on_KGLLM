import json
from neo4j import GraphDatabase

class KnowledgeGraphChecker:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_node_types(self):
        """获取所有节点类型及其数量"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n) as labels, count(n) as count
                ORDER BY count DESC
            """)
            node_types = {}
            for record in result:
                label = record["labels"][0] if record["labels"] else "Unknown"
                count = record["count"]
                node_types[label] = count
            return node_types
    
    def get_relationship_types(self):
        """获取所有关系类型及其数量"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            rel_types = {}
            for record in result:
                rel_types[record["type"]] = record["count"]
            return rel_types
    
    def get_total_nodes(self):
        """获取节点总数"""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            return result.single()["count"]
    
    def get_total_relationships(self):
        """获取关系总数"""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()["count"]
    
    def get_source_files(self):
        """获取所有源文件"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.source IS NOT NULL
                RETURN DISTINCT n.source as source
            """)
            sources = [record["source"] for record in result]
            return sources
    
    def check_coverage(self, json_file):
        """检查知识覆盖率"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        json_nodes = set(node['id'] for node in data.get('nodes', []))
        json_rels = len(data.get('relationships', []))
        
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN n.id as id")
            db_nodes = set(record["id"] for record in result)
        
        coverage = len(json_nodes & db_nodes) / len(json_nodes) * 100 if json_nodes else 0
        
        return {
            "json_nodes": len(json_nodes),
            "db_nodes": len(db_nodes),
            "matched_nodes": len(json_nodes & db_nodes),
            "coverage": coverage
        }

def main():
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "hedaiyu123"
    
    json_file = r"D:\last_school\Python_ITS_Based_on_KGLLM\Knowledge\bulid\enhanced_knowledge_graph.json"
    
    checker = KnowledgeGraphChecker(uri, user, password)
    
    try:
        print("=" * 60)
        print("知识图谱构建检查报告")
        print("=" * 60)
        
        node_types = checker.get_node_types()
        rel_types = checker.get_relationship_types()
        total_nodes = checker.get_total_nodes()
        total_rels = checker.get_total_relationships()
        sources = checker.get_source_files()
        coverage_info = checker.check_coverage(json_file)
        
        print(f"\n【节点类型统计】 (共 {len(node_types)} 类)")
        print("-" * 40)
        for label, count in node_types.items():
            print(f"  {label}: {count} 个节点")
        
        print(f"\n【关系类型统计】 (共 {len(rel_types)} 种)")
        print("-" * 40)
        for rel_type, count in rel_types.items():
            print(f"  {rel_type}: {count} 条关系")
        
        print(f"\n【总体统计】")
        print("-" * 40)
        print(f"  节点总数: {total_nodes}")
        print(f"  关系总数: {total_rels}")
        print(f"  源文件数: {len(sources)}")
        
        print(f"\n【知识覆盖率】")
        print("-" * 40)
        print(f"  JSON文件节点数: {coverage_info['json_nodes']}")
        print(f"  数据库节点数: {coverage_info['db_nodes']}")
        print(f"  匹配节点数: {coverage_info['matched_nodes']}")
        print(f"  覆盖率: {coverage_info['coverage']:.2f}%")
        
        print("\n" + "=" * 60)
        print("【要求检查结果】")
        print("=" * 60)
        
        req1 = len(node_types) >= 8
        req2 = len(rel_types) >= 5
        req3 = coverage_info['coverage'] >= 90
        
        print(f"\n1. 核心知识节点类型 ≥ 8 类: {'✓ 达标' if req1 else '✗ 未达标'} (当前: {len(node_types)} 类)")
        print(f"2. 关系类型 ≥ 5 种: {'✓ 达标' if req2 else '✗ 未达标'} (当前: {len(rel_types)} 种)")
        print(f"3. 知识覆盖率 ≥ 90%: {'✓ 达标' if req3 else '✗ 未达标'} (当前: {coverage_info['coverage']:.2f}%)")
        
        if req1 and req2 and req3:
            print("\n>>> 所有要求均已达标！")
        else:
            print("\n>>> 存在未达标项目，需要改进。")
        
    finally:
        checker.close()

if __name__ == "__main__":
    main()
