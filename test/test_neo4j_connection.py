import asyncio
from neo4j import GraphDatabase
from config.settings import settings

async def test_neo4j_connection():
    """测试Neo4j连接状态"""
    print("测试Neo4j连接状态...")
    
    # 检查Neo4j配置
    print(f"Neo4j URI: {settings.neo4j_uri}")
    print(f"Neo4j User: {settings.neo4j_user}")
    print(f"Neo4j Password: {'***' if settings.neo4j_password else '空'}")
    
    # 尝试连接到Neo4j
    driver = None
    try:
        print("\n尝试连接到Neo4j数据库...")
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
        
        # 测试连接
        with driver.session() as session:
            # 执行一个简单的查询
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            record = result.single()
            if record:
                node_count = record["node_count"]
                print(f"连接成功！数据库中有 {node_count} 个节点")
                
                # 尝试获取一些节点信息
                print("\n尝试获取前5个节点:")
                result = session.run("MATCH (n) RETURN n.id, n.name, labels(n) as labels LIMIT 5")
                nodes = []
                for record in result:
                    node_info = {
                        "id": record.get("n.id"),
                        "name": record.get("n.name"),
                        "labels": record.get("labels")
                    }
                    nodes.append(node_info)
                print(f"获取到 {len(nodes)} 个节点:")
                for node in nodes:
                    print(f"  - {node}")
            else:
                print("连接成功，但无法获取节点数量")
                
    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        if driver:
            try:
                driver.close()
                print("\n连接已关闭")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(test_neo4j_connection())