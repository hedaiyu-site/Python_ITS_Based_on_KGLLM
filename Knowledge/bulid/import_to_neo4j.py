import json
from neo4j import GraphDatabase

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def import_data(self, data_file):
        """导入知识图谱数据到neo4j"""
        # 读取数据
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = data.get('nodes', [])
        relationships = data.get('relationships', [])
        
        print(f"开始导入数据...")
        print(f"节点数量: {len(nodes)}")
        print(f"关系数量: {len(relationships)}")
        
        # 导入节点
        with self.driver.session() as session:
            print("\n导入节点中...")
            for i, node in enumerate(nodes, 1):
                if i % 50 == 0:
                    print(f"已导入节点: {i}/{len(nodes)}")
                
                session.run(
                    "CREATE (n:{node_type} {{id: $id, name: $name, source: $source}})".format(
                        node_type=node['type']
                    ),
                    id=node['id'],
                    name=node['name'],
                    source=node['source']
                )
            
            print("\n导入关系中...")
            for i, rel in enumerate(relationships, 1):
                if i % 50 == 0:
                    print(f"已导入关系: {i}/{len(relationships)}")
                
                session.run(
                    "MATCH (a), (b) WHERE a.id = $start_id AND b.id = $end_id "
                    "CREATE (a)-[r:{rel_type} {{id: $rel_id}}]->(b)".format(
                        rel_type=rel['type']
                    ),
                    start_id=rel['start_id'],
                    end_id=rel['end_id'],
                    rel_id=rel['id']
                )
        
        print("\n数据导入完成！")

if __name__ == "__main__":
    # 连接信息
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "12345678"
    
    data_file = "knowledge_graph.json"
    
    importer = Neo4jImporter(uri, user, password)
    
    try:
        importer.import_data(data_file)
    finally:
        importer.close()
