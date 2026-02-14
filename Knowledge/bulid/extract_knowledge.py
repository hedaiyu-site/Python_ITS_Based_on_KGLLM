import os
import re
import json
from typing import List, Dict, Tuple

class KnowledgeExtractor:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.nodes = []
        self.relationships = []
        self.node_id = 0
        self.relationship_id = 0
        self.node_map = {}
    
    def get_file_list(self) -> List[str]:
        """从目录.md文件获取文件列表"""
        directory_file = os.path.join(self.base_dir, "目录.md")
        files = []
        
        if os.path.exists(directory_file):
            with open(directory_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines[1:]:  # 跳过第一行标题
                if line.strip():
                    # 提取文件名
                    match = re.search(r'\[.*?\]\((.*?)\)', line)
                    if match:
                        # 清理文件名（移除%%20等编码）
                        file_name = match.group(1).replace('%%20', '').strip()
                        if file_name.endswith('.md'):
                            files.append(file_name)
        
        return files
    
    def extract_nodes_from_file(self, file_name: str, content: str) -> None:
        """从单个文件中提取知识节点"""
        # 提取文件标题作为主题节点
        title_match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
        if title_match:
            topic = title_match.group(1).strip()
            topic_id = self.add_node(topic, "Topic", file_name)
        else:
            topic = file_name.replace('.md', '')
            topic_id = self.add_node(topic, "Topic", file_name)
        
        # 提取二级标题作为子主题
        subtopics = re.findall(r'^##\s+(.*)$', content, re.MULTILINE)
        for subtopic in subtopics:
            subtopic_id = self.add_node(subtopic.strip(), "Subtopic", file_name)
            self.add_relationship(topic_id, subtopic_id, "HAS_SUBTOPIC")
        
        # 提取Python模块
        modules = re.findall(r'Python\s+(\w+)\s+模块', content)
        for module in modules:
            module_id = self.add_node(module.strip(), "Module", file_name)
            self.add_relationship(topic_id, module_id, "HAS_MODULE")
        
        # 提取函数
        functions = re.findall(r'`(\w+)\(.*?\)`', content)
        for func in functions:
            func_id = self.add_node(func.strip(), "Function", file_name)
            self.add_relationship(topic_id, func_id, "HAS_FUNCTION")
        
        # 提取关键字
        keywords = re.findall(r'\*(\w+)\*', content)
        for keyword in keywords:
            if len(keyword) > 2:  # 过滤太短的关键字
                keyword_id = self.add_node(keyword.strip(), "Keyword", file_name)
                self.add_relationship(topic_id, keyword_id, "HAS_KEYWORD")
    
    def add_node(self, name: str, node_type: str, source: str) -> int:
        """添加节点，避免重复"""
        key = f"{name}_{node_type}"
        if key not in self.node_map:
            self.node_id += 1
            self.node_map[key] = self.node_id
            self.nodes.append({
                "id": self.node_id,
                "name": name,
                "type": node_type,
                "source": source
            })
        return self.node_map[key]
    
    def add_relationship(self, start_id: int, end_id: int, rel_type: str) -> None:
        """添加关系"""
        self.relationship_id += 1
        self.relationships.append({
            "id": self.relationship_id,
            "start_id": start_id,
            "end_id": end_id,
            "type": rel_type
        })
    
    def process_all_files(self) -> None:
        """处理所有md文件"""
        files = self.get_file_list()
        
        if not files:
            # 如果目录.md不存在或为空，遍历所有md文件
            files = [f for f in os.listdir(self.base_dir) if f.endswith('.md') and f != '目录.md']
        
        for file_name in files:
            file_path = os.path.join(self.base_dir, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.extract_nodes_from_file(file_name, content)
                    print(f"处理完成: {file_name}")
                except Exception as e:
                    print(f"处理文件 {file_name} 时出错: {e}")
    
    def save_results(self) -> None:
        """保存提取结果"""
        results = {
            "nodes": self.nodes,
            "relationships": self.relationships
        }
        
        with open(os.path.join(self.base_dir, "knowledge_graph.json"), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n提取完成！")
        print(f"节点数量: {len(self.nodes)}")
        print(f"关系数量: {len(self.relationships)}")
        print(f"结果已保存到 knowledge_graph.json")

if __name__ == "__main__":
    extractor = KnowledgeExtractor("c:\\hedaiyu\\demo")
    extractor.process_all_files()
    extractor.save_results()
