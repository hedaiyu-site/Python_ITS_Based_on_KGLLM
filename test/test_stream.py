"""
流式响应测试脚本

测试FastAPI流式对话接口的响应时间和输出效果

测试内容:
- 学习路径问题的流式响应
- 首字响应时间测量
- 总响应时间测量
"""

import requests
import json
import time

url = "http://localhost:8000/chat/stream"
data = {"message": "Python初学者学习路径"}

print("测试学习路径问题...")
print("=" * 60)
start_time = time.time()
first_chunk_time = None

response = requests.post(url, json=data, stream=True)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            content = line[6:]
            if content == '[DONE]':
                break
            try:
                json_data = json.loads(content)
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    print(f"\n首字响应时间: {(first_chunk_time - start_time)*1000:.0f}ms\n")
                print(json_data['content'], end='', flush=True)
            except:
                pass

print(f"\n\n总响应时间: {(time.time() - start_time)*1000:.0f}ms")
