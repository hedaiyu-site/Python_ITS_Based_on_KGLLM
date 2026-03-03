import os
import re
import json
from typing import List, Dict, Set

class EnhancedKnowledgeExtractor:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.nodes = []
        self.relationships = []
        self.node_id = 0
        self.relationship_id = 0
        self.node_map = {}
        
        self.node_types = set()
        self.rel_types = set()
    
    def get_file_list(self) -> List[str]:
        files = []
        directory_file = os.path.join(self.base_dir, "目录.md")
        
        if os.path.exists(directory_file):
            with open(directory_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines[1:]:
                if line.strip():
                    match = re.search(r'\[.*?\]\((.*?)\)', line)
                    if match:
                        file_name = match.group(1).replace('%%20', '').strip()
                        if file_name.endswith('.md'):
                            files.append(file_name)
        
        if not files:
            files = [f for f in os.listdir(self.base_dir) if f.endswith('.md') and f != '目录.md']
        
        return files
    
    def add_node(self, name: str, node_type: str, source: str, content: str = "") -> int:
        if not name or len(name.strip()) < 2:
            return -1
        
        name = name.strip()
        key = f"{name}_{node_type}"
        
        if key not in self.node_map:
            self.node_id += 1
            self.node_map[key] = self.node_id
            self.nodes.append({
                "id": self.node_id,
                "name": name,
                "type": node_type,
                "source": source,
                "content": content
            })
            self.node_types.add(node_type)
        
        return self.node_map[key]
    
    def add_relationship(self, start_id: int, end_id: int, rel_type: str) -> None:
        if start_id == -1 or end_id == -1 or start_id == end_id:
            return
        
        key = f"{start_id}_{end_id}_{rel_type}"
        if not hasattr(self, '_rel_map'):
            self._rel_map = set()
        
        if key in self._rel_map:
            return
        
        self._rel_map.add(key)
        self.relationship_id += 1
        self.relationships.append({
            "id": self.relationship_id,
            "start_id": start_id,
            "end_id": end_id,
            "type": rel_type
        })
        self.rel_types.add(rel_type)
    
    def extract_concepts(self, content: str, topic_id: int, source: str) -> None:
        concepts = [
            "变量", "常量", "函数", "类", "对象", "方法", "属性",
            "继承", "封装", "多态", "循环", "条件", "异常", "模块",
            "包", "装饰器", "生成器", "迭代器", "闭包", "递归",
            "列表", "字典", "元组", "集合", "字符串", "整数", "浮点数",
            "布尔值", "空值", "类型注解", "匿名函数", "回调函数",
            "异步", "并发", "并行", "线程", "进程", "协程",
            "文件操作", "网络编程", "数据库", "API", "框架"
        ]
        
        for concept in concepts:
            if concept in content:
                concept_id = self.add_node(concept, "Concept", source)
                if concept_id != -1:
                    self.add_relationship(topic_id, concept_id, "HAS_CONCEPT")
    
    def extract_data_types(self, content: str, topic_id: int, source: str) -> None:
        data_types = [
            "int", "float", "str", "bool", "list", "dict", "tuple", "set",
            "None", "bytes", "bytearray", "complex", "frozenset", "range",
            "整数", "浮点数", "字符串", "布尔", "列表", "字典", "元组", "集合"
        ]
        
        for dtype in data_types:
            pattern = rf'\b{re.escape(dtype)}\b'
            if re.search(pattern, content):
                dtype_id = self.add_node(dtype, "DataType", source)
                if dtype_id != -1:
                    self.add_relationship(topic_id, dtype_id, "HAS_DATATYPE")
    
    def extract_errors(self, content: str, topic_id: int, source: str) -> None:
        error_patterns = [
            (r'(\w+Error)', "Error"),
            (r'(\w+Exception)', "Exception"),
            (r'错误[:：]\s*([^\n。！？]+)', "Error"),
        ]
        
        for pattern, error_type in error_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 3 and len(match) < 50:
                    error_id = self.add_node(match.strip(), error_type, source)
                    if error_id != -1:
                        self.add_relationship(topic_id, error_id, "HAS_ERROR")
    
    def extract_examples(self, content: str, topic_id: int, source: str) -> None:
        code_blocks = re.findall(r'```(?:python)?\s*\n(.*?)```', content, re.DOTALL)
        
        for i, code in enumerate(code_blocks[:3]):
            if len(code.strip()) > 10:
                example_name = f"示例{i+1}"
                code_preview = code.strip()[:200]
                example_id = self.add_node(example_name, "Example", source, code_preview)
                if example_id != -1:
                    self.add_relationship(topic_id, example_id, "HAS_EXAMPLE")
    
    def extract_best_practices(self, content: str, topic_id: int, source: str) -> None:
        patterns = [
            r'(?:建议|推荐|最佳实践|注意|提示)[:：]\s*([^\n。！？]+)',
            r'(?:应该|最好|避免|不要)\s*([^\n。！？]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 5 and len(match) < 100:
                    bp_id = self.add_node(match.strip(), "BestPractice", source)
                    if bp_id != -1:
                        self.add_relationship(topic_id, bp_id, "HAS_BESTPRACTICE")
    
    def extract_prerequisites(self, content: str, topic_id: int, source: str) -> None:
        prereq_patterns = [
            r'(?:前置知识|先决条件|需要先|前提)[:：]\s*([^\n。]+)',
            r'(?:需要|必须)(?:先)?(?:学习|了解|掌握)\s*([^\n。]+)',
        ]
        
        for pattern in prereq_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 2 and len(match) < 50:
                    prereq_id = self.add_node(match.strip(), "Prerequisite", source)
                    if prereq_id != -1:
                        self.add_relationship(topic_id, prereq_id, "REQUIRES")
    
    def extract_operators(self, content: str, topic_id: int, source: str) -> None:
        operators = [
            "+", "-", "*", "/", "//", "%", "**", "=", "==", "!=", 
            "<", ">", "<=", ">=", "and", "or", "not", "in", "is",
            "&", "|", "^", "~", "<<", ">>", "+=", "-=", "*=", "/="
        ]
        
        operator_contexts = re.findall(r'[`\s]([+\-*/%=<>!&|^~]+)[`\s]', content)
        
        for op in operators:
            if op in content:
                op_id = self.add_node(op, "Operator", source)
                if op_id != -1:
                    self.add_relationship(topic_id, op_id, "HAS_OPERATOR")
    
    def extract_control_structures(self, content: str, topic_id: int, source: str) -> None:
        structures = {
            "if": "条件语句",
            "else": "条件语句",
            "elif": "条件语句",
            "for": "循环语句",
            "while": "循环语句",
            "break": "循环控制",
            "continue": "循环控制",
            "pass": "占位语句",
            "try": "异常处理",
            "except": "异常处理",
            "finally": "异常处理",
            "with": "上下文管理",
            "as": "别名",
            "def": "函数定义",
            "class": "类定义",
            "return": "返回语句",
            "yield": "生成器",
            "lambda": "匿名函数",
            "import": "模块导入",
            "from": "模块导入",
        }
        
        for keyword, category in structures.items():
            pattern = rf'\b{keyword}\b'
            if re.search(pattern, content):
                cs_name = f"{keyword}({category})"
                cs_id = self.add_node(cs_name, "ControlStructure", source)
                if cs_id != -1:
                    self.add_relationship(topic_id, cs_id, "HAS_CONTROLSTRUCTURE")
    
    def extract_modules(self, content: str, topic_id: int, source: str) -> None:
        module_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)',
            r'(\w+)\s+模块',
        ]
        
        for pattern in module_patterns:
            matches = re.findall(pattern, content)
            for module in matches:
                if len(module) > 1 and module not in ['the', 'a', 'an', 'is', 'are']:
                    module_id = self.add_node(module.strip(), "Module", source)
                    if module_id != -1:
                        self.add_relationship(topic_id, module_id, "HAS_MODULE")
    
    def extract_functions(self, content: str, topic_id: int, source: str) -> None:
        func_patterns = [
            r'`(\w+)\([^)]*\)`',
            r'(\w+)\([^)]*\)\s*[：:\(]',
            r'函数[：:]\s*(\w+)',
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            for func in matches:
                if len(func) > 1 and len(func) < 30:
                    func_id = self.add_node(func.strip(), "Function", source)
                    if func_id != -1:
                        self.add_relationship(topic_id, func_id, "HAS_FUNCTION")
    
    def extract_keywords(self, content: str, topic_id: int, source: str) -> None:
        keyword_patterns = [
            r'\*\*([^*]+)\*\*',
            r'`([^`]+)`',
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, content)
            for keyword in matches:
                keyword = keyword.strip()
                if len(keyword) > 2 and len(keyword) < 30:
                    if not re.match(r'^[+\-*/%=<>!&|^~]+$', keyword):
                        keyword_id = self.add_node(keyword, "Keyword", source)
                        if keyword_id != -1:
                            self.add_relationship(topic_id, keyword_id, "HAS_KEYWORD")
    
    def build_knowledge_relations(self) -> None:
        topics = {n['id']: n for n in self.nodes if n['type'] == 'Topic'}
        concepts = {n['id']: n for n in self.nodes if n['type'] == 'Concept'}
        
        for concept_id, concept in concepts.items():
            for topic_id, topic in topics.items():
                if concept['name'] in topic.get('name', ''):
                    self.add_relationship(topic_id, concept_id, "RELATED_TO")
    
    def extract_nodes_from_file(self, file_name: str, content: str) -> None:
        title_match = re.search(r'^#\s+(.*)$', content, re.MULTILINE)
        if title_match:
            topic = title_match.group(1).strip()
        else:
            topic = file_name.replace('.md', '')
        
        topic_id = self.add_node(topic, "Topic", file_name)
        if topic_id == -1:
            return
        
        subtopics = re.findall(r'^##\s+(.*)$', content, re.MULTILINE)
        for subtopic in subtopics:
            subtopic_id = self.add_node(subtopic.strip(), "Subtopic", file_name)
            if subtopic_id != -1:
                self.add_relationship(topic_id, subtopic_id, "HAS_SUBTOPIC")
        
        self.extract_concepts(content, topic_id, file_name)
        self.extract_data_types(content, topic_id, file_name)
        self.extract_errors(content, topic_id, file_name)
        self.extract_examples(content, topic_id, file_name)
        self.extract_best_practices(content, topic_id, file_name)
        self.extract_prerequisites(content, topic_id, file_name)
        self.extract_operators(content, topic_id, file_name)
        self.extract_control_structures(content, topic_id, file_name)
        self.extract_modules(content, topic_id, file_name)
        self.extract_functions(content, topic_id, file_name)
        self.extract_keywords(content, topic_id, file_name)
    
    def process_all_files(self) -> None:
        files = self.get_file_list()
        
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
        
        self.build_knowledge_relations()
    
    def save_results(self) -> None:
        results = {
            "nodes": self.nodes,
            "relationships": self.relationships
        }
        
        output_path = os.path.join(os.path.dirname(self.base_dir), "bulid", "enhanced_knowledge_graph.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*60}")
        print("知识图谱构建完成！")
        print(f"{'='*60}")
        print(f"节点总数: {len(self.nodes)}")
        print(f"关系总数: {len(self.relationships)}")
        print(f"\n节点类型 ({len(self.node_types)}种):")
        for nt in sorted(self.node_types):
            count = sum(1 for n in self.nodes if n['type'] == nt)
            print(f"  {nt}: {count}")
        print(f"\n关系类型 ({len(self.rel_types)}种):")
        for rt in sorted(self.rel_types):
            count = sum(1 for r in self.relationships if r['type'] == rt)
            print(f"  {rt}: {count}")
        print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    base_dir = r"D:\last_school\Python_ITS_Based_on_KGLLM\Knowledge\md"
    extractor = EnhancedKnowledgeExtractor(base_dir)
    extractor.process_all_files()
    extractor.save_results()
