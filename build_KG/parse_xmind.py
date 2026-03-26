"""
XMind文件解析模块

提供XMind脑图文件的解析功能
将XMind文件中的层级结构转换为Python字典格式

主要功能:
- 解析XMind文件(ZIP格式)
- 提取主题层级结构
- 打印主题树形结构

XMind文件结构:
- XMind文件本质是ZIP压缩包
- 包含content.json文件存储脑图数据
- 根主题(rootTopic)下包含多个子主题

作者: Python学习助手团队
版本: 1.0.0
"""

import zipfile
import json
import os


def parse_xmind(xmind_path):
    """
    解析XMind文件
    
    读取XMind文件并提取所有主题结构
    
    Args:
        xmind_path: XMind文件路径
    
    Returns:
        主题列表，每个主题是一个嵌套字典
    """
    topics = []
    with zipfile.ZipFile(xmind_path, 'r') as z:
        for file_name in z.namelist():
            if file_name.endswith('.json'):
                with z.open(file_name) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if 'rootTopic' in item:
                                topics.append(extract_topics(item['rootTopic']))
                    elif 'rootTopic' in data:
                        topics.append(extract_topics(data['rootTopic']))
    return topics


def extract_topics(topic, level=0):
    """
    递归提取主题结构
    
    将XMind主题转换为标准字典格式
    
    Args:
        topic: XMind主题对象
        level: 当前层级(用于缩进显示)
    
    Returns:
        包含title、level、children的字典
    """
    result = {
        'title': topic.get('title', ''),
        'level': level,
        'children': []
    }
    
    children = topic.get('children', {})
    attached = children.get('attached', [])
    
    for child in attached:
        result['children'].append(extract_topics(child, level + 1))
    
    return result


def print_topics(topic, indent=0):
    """
    打印主题树形结构
    
    以缩进形式显示主题层级
    
    Args:
        topic: 主题字典
        indent: 缩进级别
    """
    print('  ' * indent + topic['title'])
    for child in topic['children']:
        print_topics(child, indent + 1)


if __name__ == '__main__':
    """
    主函数
    
    解析并打印Python基础教程和高级教程的脑图结构
    """
    base_path = r'd:\project\RAG\知识图谱脑图'
    
    print("=" * 60)
    print("Python基础编程教程")
    print("=" * 60)
    basic_file = os.path.join(base_path, 'Python基础编程教程_ima脑图.xmind')
    basic_topics = parse_xmind(basic_file)
    for topic in basic_topics:
        print_topics(topic)
    
    print("\n" + "=" * 60)
    print("Python高级教程")
    print("=" * 60)
    advanced_file = os.path.join(base_path, 'Python高级教程思维导图大纲_ima脑图.xmind')
    advanced_topics = parse_xmind(advanced_file)
    for topic in advanced_topics:
        print_topics(topic)
