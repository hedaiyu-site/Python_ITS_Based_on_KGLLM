import json
from neo4j import GraphDatabase

class EnhancedNeo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """清空数据库"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")
    
    def import_data(self, data_file):
        """导入知识图谱数据到neo4j"""
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        relationships = data.get('relationships', [])
        
        print(f"开始导入数据...")
        print(f"节点数量: {len(nodes)}")
        print(f"关系数量: {len(relationships)}")
        
        with self.driver.session() as session:
            print("\n导入节点中...")
            batch_size = 100
            for i in range(0, len(nodes), batch_size):
                batch = nodes[i:i+batch_size]
                for node in batch:
                    session.run(
                        f"MERGE (n:{node['type']} {{id: $id}}) "
                        "SET n.name = $name, n.source = $source, n.content = $content",
                        id=node['id'],
                        name=node['name'],
                        source=node.get('source', ''),
                        content=node.get('content', '')
                    )
                if (i + batch_size) % 500 == 0 or i + batch_size >= len(nodes):
                    print(f"已导入节点: {min(i + batch_size, len(nodes))}/{len(nodes)}")
            
            print("\n导入关系中...")
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i:i+batch_size]
                for rel in batch:
                    session.run(
                        f"MATCH (a {{id: $start_id}}), (b {{id: $end_id}}) "
                        f"MERGE (a)-[r:{rel['type']}]->(b)",
                        start_id=rel['start_id'],
                        end_id=rel['end_id']
                    )
                if (i + batch_size) % 500 == 0 or i + batch_size >= len(relationships):
                    print(f"已导入关系: {min(i + batch_size, len(relationships))}/{len(relationships)}")
        
        print("\n数据导入完成！")

if __name__ == "__main__":
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "hedaiyu123"
    
    data_file = r"D:\last_school\Python_ITS_Based_on_KGLLM\Knowledge\bulid\enhanced_knowledge_graph.json"
    
    importer = EnhancedNeo4jImporter(uri, user, password)
    
    try:
        importer.clear_database()
        importer.import_data(data_file)
    finally:
        importer.close()
