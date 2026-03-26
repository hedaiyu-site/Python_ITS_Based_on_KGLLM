"""
导出知识图谱中所有知识点

统计并导出Neo4j知识图谱中的所有知识点
"""

from neo4j import GraphDatabase
import json
import os
from datetime import datetime
from collections import defaultdict

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hedaiyu123"
NEO4J_DATABASE = "neo4j"

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def export_knowledge_points():
    driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_knowledge_points = {}
    type_statistics = defaultdict(int)
    
    with driver.session(database=NEO4J_DATABASE) as session:
        print("=" * 70)
        print("Neo4j 知识图谱 - 知识点统计与导出")
        print("=" * 70)
        
        node_types = [
            "KnowledgePoint", "DataType", "Module", "Function", 
            "Concept", "ControlStructure", "Operator", "Library", "Tool"
        ]
        
        print("\n【各类型知识点统计】")
        print("-" * 40)
        
        total_count = 0
        for node_type in node_types:
            result = session.run(f"MATCH (n:{node_type}) RETURN n.name as name, n.id as id ORDER BY n.name")
            nodes = list(result)
            count = len(nodes)
            
            if count > 0:
                type_statistics[node_type] = count
                total_count += count
                print(f"  {node_type}: {count} 个")
                
                all_knowledge_points[node_type] = []
                for node in nodes:
                    all_knowledge_points[node_type].append({
                        "id": node["id"],
                        "name": node["name"]
                    })
        
        print("-" * 40)
        print(f"  【知识点总数】: {total_count} 个")
        
        print("\n【课程与章节结构】")
        print("-" * 40)
        
        result = session.run("""
            MATCH (c:Course)-[:HAS_CHAPTER]->(ch:Chapter)
            OPTIONAL MATCH (ch)-[:HAS_SECTION]->(s:Section)
            RETURN c.name as course, c.id as course_id, 
                   ch.name as chapter, ch.id as chapter_id,
                   collect(s.name) as sections
            ORDER BY chapter_id
        """)
        
        course_structure = []
        for r in result:
            course_info = {
                "course": r["course"],
                "chapter": r["chapter"],
                "sections": r["sections"] if r["sections"] else []
            }
            course_structure.append(course_info)
            print(f"  课程: {r['course']}")
            print(f"    章节: {r['chapter']}")
            if r["sections"]:
                for sec in r["sections"][:3]:
                    print(f"      - {sec}")
                if len(r["sections"]) > 3:
                    print(f"      ... 等 {len(r['sections'])} 个小节")
        
        print("\n【关系类型统计】")
        print("-" * 40)
        result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        all_rel_types = [r["relationshipType"] for r in result]
        
        rel_statistics = {}
        for rt in all_rel_types:
            result = session.run(f"MATCH ()-[r:{rt}]->() RETURN count(r) as count")
            count = result.single()["count"]
            if count > 0:
                rel_statistics[rt] = count
                print(f"  {rt}: {count} 条")
        
        print("\n" + "=" * 70)
        print("【导出结果】")
        
        export_data = {
            "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "statistics": {
                "total_knowledge_points": total_count,
                "by_type": dict(type_statistics),
                "relations": rel_statistics
            },
            "knowledge_points": all_knowledge_points,
            "course_structure": course_structure
        }
        
        json_path = os.path.join(OUTPUT_DIR, "knowledge_points.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"  JSON文件: {json_path}")
        
        txt_path = os.path.join(OUTPUT_DIR, "knowledge_points.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("知识图谱知识点列表\n")
            f.write(f"导出时间: {export_data['export_time']}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"知识点总数: {total_count} 个\n\n")
            
            for node_type, points in all_knowledge_points.items():
                f.write(f"\n【{node_type}】({len(points)} 个)\n")
                f.write("-" * 40 + "\n")
                for i, point in enumerate(points, 1):
                    f.write(f"  {i}. {point['name']}")
                    if point['id']:
                        f.write(f" (id: {point['id']})")
                    f.write("\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("【课程结构】\n")
            f.write("=" * 70 + "\n")
            for cs in course_structure:
                f.write(f"\n课程: {cs['course']}\n")
                f.write(f"  章节: {cs['chapter']}\n")
                for sec in cs['sections']:
                    f.write(f"    - {sec}\n")
        
        print(f"  TXT文件: {txt_path}")
        
        csv_path = os.path.join(OUTPUT_DIR, "knowledge_points.csv")
        with open(csv_path, "w", encoding="utf-8-sig") as f:
            f.write("序号,类型,名称,ID\n")
            idx = 1
            for node_type, points in all_knowledge_points.items():
                for point in points:
                    f.write(f'{idx},"{node_type}","{point["name"]}","{point["id"] or ""}"\n')
                    idx += 1
        print(f"  CSV文件: {csv_path}")
        
        print("\n" + "=" * 70)
        print("导出完成!")
        print("=" * 70)
    
    driver.close()
    return export_data


if __name__ == "__main__":
    export_knowledge_points()
