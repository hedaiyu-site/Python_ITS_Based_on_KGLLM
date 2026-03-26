"""
Python知识图谱构建脚本

从XMind脑图文件解析Python教程内容并构建Neo4j知识图谱

主要功能:
- 解析XMind格式的Python教程脑图
- 自动分类知识点节点(12种节点类型)
- 创建知识图谱节点和关系
- 生成附加的知识关联关系

节点类型:
- Course: 课程
- Chapter: 章节
- Section: 小节
- KnowledgePoint: 知识点
- DataType: 数据类型
- Module: 模块
- Function: 函数
- Concept: 概念
- ControlStructure: 控制结构
- Operator: 运算符
- Library: 第三方库
- Tool: 工具

关系类型:
- HAS_CHAPTER: 课程包含章节
- HAS_SECTION: 章节包含小节
- HAS_KNOWLEDGE_POINT: 小节包含知识点
- HAS_SUB_POINT: 知识点包含子知识点
- RELATED_TO: 相关关系
- USED_FOR: 用途关系

作者: Python学习助手团队
版本: 1.0.0
"""

import zipfile
import json
from neo4j import GraphDatabase

NEO4J_URL = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hedaiyu123"
NEO4J_DATABASE = "neo4j"


class PythonKnowledgeGraphBuilder:
    """
    Python知识图谱构建器
    
    负责从XMind文件解析内容并构建Neo4j知识图谱
    """
    
    def __init__(self, uri, user, password, database):
        """
        初始化构建器
        
        Args:
            uri: Neo4j数据库连接地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.node_count = {}
        self.relation_count = {}
    
    def close(self):
        """关闭数据库连接"""
        self.driver.close()
    
    def clear_database(self):
        """清空数据库中的所有节点和关系"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("数据库已清空")
    
    def create_constraints(self):
        """
        创建数据库约束
        
        为各类节点创建唯一性约束，确保节点不重复
        """
        with self.driver.session(database=self.database) as session:
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Course) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (ch:Chapter) REQUIRE ch.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Section) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (kp:KnowledgePoint) REQUIRE kp.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (dt:DataType) REQUIRE dt.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Module) REQUIRE m.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Function) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (cs:ControlStructure) REQUIRE cs.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (op:Operator) REQUIRE op.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (lib:Library) REQUIRE lib.name IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE",
            ]
            for constraint in constraints:
                try:
                    session.run(constraint)
                except:
                    pass
            print("约束创建完成")
    
    def classify_node(self, title):
        """
        根据标题内容分类节点类型
        
        通过关键词匹配自动判断知识点属于哪种节点类型
        
        Args:
            title: 节点标题文本
        
        Returns:
            节点类型字符串
        """
        data_types = ['数字', '字符串', '列表', '元组', '集合', '字典', '整数', '浮点数', '复数', 
                      '布尔', 'bytes', 'bytearray']
        for dt in data_types:
            if dt in title:
                return "DataType"
        
        modules = ['sys模块', 'os模块', 'math模块', 'datetime模块', 'json模块', 're模块', 
                   'random模块', 'csv模块', 'pickle模块', 'hashlib模块', 'threading模块',
                   'asyncio模块', 'urllib模块', 'logging模块', 'statistics模块',
                   'operator模块', 'StringIO模块', 'queue模块', '_thread模块', 
                   'subprocess模块', 'time与calendar模块']
        for m in modules:
            if m in title:
                return "Module"
        
        libraries = ['requests模块', 'BeautifulSoup', 'Scrapy', 'selenium', 'PyQt',
                     'pyecharts', 'OpenAI', 'mysql-connector', 'PyMySQL', 
                     'MongoDB', 'uWSGI']
        for lib in libraries:
            if lib in title:
                return "Library"
        
        functions = ['print函数', 'input函数', 'open函数', 'range()', 'map', 'filter', 
                     'reduce', 'lambda', 'yield']
        for f in functions:
            if f in title.lower():
                return "Function"
        
        control_structures = ['if', 'elif', 'else', 'while循环', 'for循环', 'break', 
                              'continue', 'pass', 'try', 'except', 'finally', 'with', 
                              'match', 'case', '循环控制']
        for cs in control_structures:
            if cs in title.lower():
                return "ControlStructure"
        
        operators = ['运算符', '算术运算符', '比较运算符', '赋值运算符', '逻辑运算符', 
                     '位运算符', '成员运算符', '身份运算符']
        for op in operators:
            if op in title:
                return "Operator"
        
        concepts = ['继承', '多态', '封装', '装饰器', '迭代器', '生成器', '类与对象', 
                    '属性与方法', '匿名函数', '推导式', '上下文管理', '命名空间', '作用域',
                    '异常处理', '面向对象', '函数式编程', '网络编程', '正则表达式', 
                    '并发', '并行', '进程管理', '多线程', '异步编程', 'SMTP', 'XML解析',
                    'Markdown', '量化金融', 'AI绘画', 'AI模型调用']
        for c in concepts:
            if c in title:
                return "Concept"
        
        tools = ['pip', 'VScode', 'venv', '虚拟环境']
        for t in tools:
            if t in title:
                return "Tool"
        
        return "KnowledgePoint"
    
    def create_node(self, session, node_id, title, node_type):
        """
        创建知识图谱节点
        
        Args:
            session: Neo4j会话
            node_id: 节点ID
            title: 节点标题/名称
            node_type: 节点类型
        """
        if node_type in ['Module', 'DataType', 'Library', 'Tool']:
            session.run(f"""
                MERGE (n:{node_type} {{name: $name}})
            """, name=title)
        else:
            session.run(f"""
                MERGE (n:{node_type} {{id: $id}})
                SET n.name = $name
            """, id=node_id, name=title)
        self.node_count[node_type] = self.node_count.get(node_type, 0) + 1
    
    def create_relation(self, session, from_id, from_type, to_id, to_type, rel_type, to_name=None, order=0):
        """
        创建节点之间的关系
        
        Args:
            session: Neo4j会话
            from_id: 起始节点ID
            from_type: 起始节点类型
            to_id: 目标节点ID
            to_type: 目标节点类型
            rel_type: 关系类型
            to_name: 目标节点名称(用于name属性节点)
            order: 顺序值
        """
        if to_type in ['Module', 'DataType', 'Library', 'Tool']:
            session.run(f"""
                MATCH (from:{from_type} {{id: $from_id}})
                MATCH (to:{to_type} {{name: $to_name}})
                MERGE (from)-[:{rel_type} {{order: $order}}]->(to)
            """, from_id=from_id, to_name=to_name, order=order)
        else:
            session.run(f"""
                MATCH (from:{from_type} {{id: $from_id}})
                MATCH (to:{to_type} {{id: $to_id}})
                MERGE (from)-[:{rel_type} {{order: $order}}]->(to)
            """, from_id=from_id, to_id=to_id, order=order)
        self.relation_count[rel_type] = self.relation_count.get(rel_type, 0) + 1
    
    def create_relation_by_name(self, session, from_name, from_type, to_name, to_type, rel_type, order=0):
        """
        通过名称创建节点之间的关系
        
        Args:
            session: Neo4j会话
            from_name: 起始节点名称
            from_type: 起始节点类型
            to_name: 目标节点名称
            to_type: 目标节点类型
            rel_type: 关系类型
            order: 顺序值
        """
        session.run(f"""
            MATCH (from:{from_type} {{name: $from_name}})
            MATCH (to:{to_type} {{name: $to_name}})
            MERGE (from)-[:{rel_type} {{order: $order}}]->(to)
        """, from_name=from_name, to_name=to_name, order=order)
        self.relation_count[rel_type] = self.relation_count.get(rel_type, 0) + 1
    
    def parse_xmind(self, xmind_path):
        """
        解析XMind文件
        
        读取XMind文件中的content.json并提取根主题
        
        Args:
            xmind_path: XMind文件路径
        
        Returns:
            根主题字典
        """
        with zipfile.ZipFile(xmind_path, 'r') as z:
            for file_name in z.namelist():
                if file_name == 'content.json':
                    with z.open(file_name) as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            return data[0].get('rootTopic', {})
        return {}
    
    def build_course(self, xmind_path, course_type):
        """
        构建课程知识图谱
        
        从XMind文件解析课程内容并创建知识图谱
        
        Args:
            xmind_path: XMind文件路径
            course_type: 课程类型('basic'或'advanced')
        """
        root_topic = self.parse_xmind(xmind_path)
        if not root_topic:
            print(f"无法解析文件: {xmind_path}")
            return
        
        course_title = "Python基础编程教程" if course_type == 'basic' else "Python高级教程"
        
        with self.driver.session(database=self.database) as session:
            course_id = f"course_{course_type}"
            self.create_node(session, course_id, course_title, "Course")
            
            children = root_topic.get('children', {}).get('attached', [])
            
            for ch_idx, chapter in enumerate(children):
                chapter_title = chapter.get('title', '').replace('\n', ' ').strip()
                chapter_id = f"{course_id}_ch_{ch_idx}"
                self.create_node(session, chapter_id, chapter_title, "Chapter")
                self.create_relation(session, course_id, "Course", chapter_id, "Chapter", "HAS_CHAPTER", order=ch_idx)
                
                sections = chapter.get('children', {}).get('attached', [])
                for sec_idx, section in enumerate(sections):
                    section_title = section.get('title', '').replace('\n', ' ').strip()
                    section_id = f"{chapter_id}_sec_{sec_idx}"
                    self.create_node(session, section_id, section_title, "Section")
                    self.create_relation(session, chapter_id, "Chapter", section_id, "Section", "HAS_SECTION", order=sec_idx)
                    
                    knowledge_points = section.get('children', {}).get('attached', [])
                    self._process_knowledge_points(session, section_id, "Section", knowledge_points, 0)
    
    def _process_knowledge_points(self, session, parent_id, parent_type, children, level):
        """
        递归处理知识点
        
        Args:
            session: Neo4j会话
            parent_id: 父节点ID
            parent_type: 父节点类型
            children: 子节点列表
            level: 当前层级
        """
        for idx, child in enumerate(children):
            title = child.get('title', '').replace('\n', ' ').strip()
            if not title:
                continue
            
            node_id = f"{parent_id}_kp_{idx}"
            node_type = self.classify_node(title)
            
            self.create_node(session, node_id, title, node_type)
            
            if level == 0:
                self.create_relation(session, parent_id, parent_type, node_id, node_type, 
                                    "HAS_KNOWLEDGE_POINT", to_name=title, order=idx)
            else:
                if parent_type in ['Module', 'DataType', 'Library', 'Tool']:
                    parent_name = parent_id
                    self.create_relation_by_name(session, parent_name, parent_type, title, node_type, 
                                                "HAS_SUB_POINT", order=idx)
                else:
                    self.create_relation(session, parent_id, parent_type, node_id, node_type, 
                                        "HAS_SUB_POINT", to_name=title, order=idx)
            
            sub_children = child.get('children', {}).get('attached', [])
            if sub_children:
                if node_type in ['Module', 'DataType', 'Library', 'Tool']:
                    self._process_knowledge_points(session, title, node_type, sub_children, level + 1)
                else:
                    self._process_knowledge_points(session, node_id, node_type, sub_children, level + 1)
    
    def create_additional_relations(self):
        """
        创建附加的知识关联关系
        
        在已有节点之间创建RELATED_TO和USED_FOR关系
        """
        with self.driver.session(database=self.database) as session:
            session.run("""
                MATCH (c1:Concept), (c2:Concept)
                WHERE c1.name = '继承' AND c2.name = '多态'
                MERGE (c1)-[:RELATED_TO]->(c2)
            """)
            session.run("""
                MATCH (c1:Concept), (c2:Concept)
                WHERE c1.name = '迭代器' AND c2.name = '生成器'
                MERGE (c1)-[:RELATED_TO]->(c2)
            """)
            session.run("""
                MATCH (dt1:DataType), (dt2:DataType)
                WHERE dt1.name = '列表' AND dt2.name = '元组'
                MERGE (dt1)-[:RELATED_TO]->(dt2)
            """)
            session.run("""
                MATCH (dt1:DataType), (dt2:DataType)
                WHERE dt1.name = '集合' AND dt2.name = '字典'
                MERGE (dt1)-[:RELATED_TO]->(dt2)
            """)
            session.run("""
                MATCH (m:Module), (c:Concept)
                WHERE m.name = 'threading模块' AND c.name CONTAINS '多线程'
                MERGE (m)-[:USED_FOR]->(c)
            """)
            session.run("""
                MATCH (m:Module), (c:Concept)
                WHERE m.name = 'asyncio模块' AND c.name CONTAINS '异步'
                MERGE (m)-[:USED_FOR]->(c)
            """)
            print("附加关系创建完成")
    
    def print_statistics(self):
        """
        打印知识图谱统计信息
        
        显示各类节点和关系的数量，并检查是否满足要求
        """
        print("\n" + "=" * 60)
        print("知识图谱统计信息")
        print("=" * 60)
        
        with self.driver.session(database=self.database) as session:
            node_types = ['Course', 'Chapter', 'Section', 'KnowledgePoint', 'DataType', 
                          'Module', 'Function', 'Concept', 'ControlStructure', 'Operator',
                          'Library', 'Tool']
            
            total_nodes = 0
            actual_node_types = []
            print("\n节点统计:")
            for node_type in node_types:
                result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                count = result.single()['count']
                if count > 0:
                    print(f"  {node_type}: {count} 个节点")
                    total_nodes += count
                    actual_node_types.append(node_type)
            
            print(f"\n总节点数: {total_nodes}")
            print(f"节点类型数量: {len(actual_node_types)} (要求≥8)")
            
            relation_types = ['HAS_CHAPTER', 'HAS_SECTION', 'HAS_KNOWLEDGE_POINT', 
                              'HAS_SUB_POINT', 'RELATED_TO', 'USED_FOR']
            
            total_relations = 0
            actual_rel_types = []
            print("\n关系统计:")
            for rel_type in relation_types:
                result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
                count = result.single()['count']
                if count > 0:
                    print(f"  {rel_type}: {count} 条关系")
                    total_relations += count
                    actual_rel_types.append(rel_type)
            
            print(f"\n总关系数: {total_relations}")
            print(f"关系类型数量: {len(actual_rel_types)} (要求≥5)")
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            all_relations = result.single()['count']
            print(f"数据库总关系数: {all_relations}")
            
            print("\n" + "=" * 60)
            print("要求检查结果:")
            if len(actual_node_types) >= 8:
                print(f"  ✓ 节点类型: {len(actual_node_types)}种 (满足≥8种要求)")
            else:
                print(f"  ✗ 节点类型: {len(actual_node_types)}种 (不满足≥8种要求)")
            
            if len(actual_rel_types) >= 5:
                print(f"  ✓ 关系类型: {len(actual_rel_types)}种 (满足≥5种要求)")
            else:
                print(f"  ✗ 关系类型: {len(actual_rel_types)}种 (不满足≥5种要求)")
            print("=" * 60)


def main():
    """
    主函数
    
    执行知识图谱构建流程:
    1. 清空数据库
    2. 创建约束
    3. 构建基础课程知识图谱
    4. 构建高级课程知识图谱
    5. 创建附加关系
    6. 打印统计信息
    """
    builder = PythonKnowledgeGraphBuilder(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    try:
        print("=" * 60)
        print("开始构建Python知识图谱")
        print("=" * 60)
        
        print("\n[1/5] 清空数据库...")
        builder.clear_database()
        
        print("[2/5] 创建约束...")
        builder.create_constraints()
        
        print("[3/5] 构建基础课程知识图谱...")
        basic_file = r'd:\Project\server\RAG\知识图谱脑图\Python基础编程教程_ima脑图.xmind'
        builder.build_course(basic_file, 'basic')
        
        print("[4/5] 构建高级课程知识图谱...")
        advanced_file = r'd:\Project\server\RAG\知识图谱脑图\Python高级教程思维导图大纲_ima脑图.xmind'
        builder.build_course(advanced_file, 'advanced')
        
        print("[5/5] 创建附加关系...")
        builder.create_additional_relations()
        
        builder.print_statistics()
        
        print("\n✓ 知识图谱构建完成!")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        builder.close()


if __name__ == '__main__':
    main()
