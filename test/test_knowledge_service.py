import asyncio
from services.knowledge_service import KnowledgeService

async def test_knowledge_service():
    """测试KnowledgeService模块"""
    knowledge_service = KnowledgeService()
    
    print("测试KnowledgeService模块...")
    
    # 测试获取节点功能
    print("\n1. 测试获取节点功能:")
    node_id = "python_basic"
    node = await knowledge_service.get_node(node_id)
    print(f"获取节点 {node_id} 结果: {node}")
    
    # 测试搜索功能
    print("\n2. 测试搜索功能:")
    search_query = "函数"
    search_results = await knowledge_service.search(search_query, limit=5)
    print(f"搜索 '{search_query}' 结果: {search_results}")
    
    # 测试获取相关节点功能
    print("\n3. 测试获取相关节点功能:")
    related_nodes = await knowledge_service.get_related_nodes(node_id)
    print(f"节点 {node_id} 的相关节点: {related_nodes}")
    
    # 测试获取节点关系功能
    print("\n4. 测试获取节点关系功能:")
    relationships = await knowledge_service.get_node_relationships(node_id)
    print(f"节点 {node_id} 的关系: {relationships}")
    
    # 测试根据类型获取节点功能
    print("\n5. 测试根据类型获取节点功能:")
    node_type = "Concept"
    nodes_by_type = await knowledge_service.get_nodes_by_type(node_type, limit=5)
    print(f"类型 '{node_type}' 的节点: {nodes_by_type}")

if __name__ == "__main__":
    asyncio.run(test_knowledge_service())