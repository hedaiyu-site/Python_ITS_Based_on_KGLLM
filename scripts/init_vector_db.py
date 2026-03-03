import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.knowledge_vector_service import KnowledgeVectorService


async def main():
    print("=" * 60)
    print("知识图谱向量化初始化脚本")
    print("=" * 60)
    
    service = KnowledgeVectorService()
    
    print("\n步骤1: 检查当前向量数据库状态...")
    stats = await service.get_stats()
    print(f"当前状态: {stats}")
    
    print("\n步骤2: 开始向量化知识图谱节点...")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    result = await service.vectorize_knowledge_graph(
        node_types=["Concept", "Topic", "Subtopic", "Example", "Operator", 
                   "ControlStructure", "Keyword", "Function", "Module"],
        batch_size=20
    )
    
    print("\n步骤3: 向量化完成!")
    print(f"总向量化节点数: {result['total_vectorized']}")
    
    if result['errors']:
        print(f"\n错误信息:")
        for error in result['errors']:
            print(f"  - {error}")
    
    print("\n步骤4: 最终向量数据库状态...")
    final_stats = await service.get_stats()
    print(f"总向量数: {final_stats['total_vectors']}")
    print(f"向量维度: {final_stats['dimension']}")
    print(f"索引类型: {final_stats['index_type']}")
    print(f"存储路径: {final_stats['db_path']}")
    
    print("\n" + "=" * 60)
    print("向量化初始化完成!")
    print("=" * 60)
    
    print("\n测试语义搜索功能...")
    test_query = "Python列表操作"
    search_results = await service.semantic_search(test_query, top_k=5)
    
    print(f"\n查询: '{test_query}'")
    print(f"找到 {len(search_results)} 个相关结果:")
    
    for i, result in enumerate(search_results, 1):
        metadata = result.get('metadata', {})
        print(f"\n{i}. {metadata.get('name', 'N/A')}")
        print(f"   类型: {metadata.get('node_type', 'N/A')}")
        print(f"   相似度: {result.get('score', 0):.4f}")


if __name__ == "__main__":
    asyncio.run(main())
