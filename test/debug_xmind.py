"""
XMind文件调试脚本

调试XMind文件的内部结构

调试内容:
- 文件列表
- JSON内容结构
- XML内容结构
"""

import zipfile
import json
import os


def debug_xmind(xmind_path):
    """
    调试XMind文件结构
    
    Args:
        xmind_path: XMind文件路径
    """
    print(f"\n调试文件: {xmind_path}")
    with zipfile.ZipFile(xmind_path, 'r') as z:
        print(f"文件列表: {z.namelist()}")
        for file_name in z.namelist():
            print(f"\n--- {file_name} ---")
            if file_name.endswith('.json'):
                with z.open(file_name) as f:
                    data = json.load(f)
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:5000])
            elif file_name.endswith('.xml'):
                with z.open(file_name) as f:
                    content = f.read().decode('utf-8')
                    print(content[:2000])


if __name__ == '__main__':
    base_path = r'd:\project\RAG\知识图谱脑图'
    
    basic_file = os.path.join(base_path, 'Python基础编程教程_ima脑图.xmind')
    debug_xmind(basic_file)
    
    advanced_file = os.path.join(base_path, 'Python高级教程思维导图大纲_ima脑图.xmind')
    debug_xmind(advanced_file)
