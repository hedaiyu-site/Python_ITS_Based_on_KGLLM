"""
XMind文件章节检查脚本

检查XMind文件中的章节列表

检查内容:
- 基础课程章节列表
- 章节顺序和索引
"""

import zipfile
import json

xmind_path = r'd:\project\RAG\知识图谱脑图\Python基础编程教程_ima脑图.xmind'

with zipfile.ZipFile(xmind_path, 'r') as z:
    for file_name in z.namelist():
        if file_name == 'content.json':
            with z.open(file_name) as f:
                data = json.load(f)
                root = data[0]['rootTopic']
                children = root.get('children', {}).get('attached', [])
                
                print("基础课程章节列表:")
                for idx, ch in enumerate(children):
                    title = ch.get('title', '').replace('\n', ' ').strip()
                    print(f"  [{idx}] {title}")
