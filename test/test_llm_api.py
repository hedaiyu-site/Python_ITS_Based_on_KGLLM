import os
from openai import OpenAI
client = OpenAI(
   api_key="sk-b40dc8abd15446e1b36464a10be57eee",
   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
completion = client.chat.completions.create(
   model="qwen-plus",
   messages=[
       {"role": "system", "content": "You are a helpful assistant."},
       {"role": "user", "content": "阿里云公司的简介"}
   ],
   stream=True
)
for chunk in completion:
   print(chunk.choices[0].delta.content, end="", flush=True)