"""测试API服务"""

import subprocess
import time
import sys
import requests

# 启动服务
proc = subprocess.Popen([sys.executable, 'agent.py', 'serve'], 
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)

# 测试多个query
queries = [
    '查技术部员工',
    '什么是RAG',
    '列出当前目录的文件'
]

print("=" * 50)
print("AgentX API 测试")
print("=" * 50)

for q in queries:
    try:
        r = requests.post('http://localhost:8001/chat', json={'message': q}, timeout=10)
        data = r.json()
        print(f"\nQ: {q}")
        print(f"Intent: {data['intent']}, Tool: {data['tool']}")
        print(f"Answer: {data['answer'][:150]}...")
    except Exception as e:
        print(f"Error: {e}")

proc.terminate()

print("\n" + "=" * 50)
print("API 测试完成!")
print("=" * 50)