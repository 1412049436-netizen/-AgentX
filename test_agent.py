"""测试AgentX"""

from agent import get_agent

agent = get_agent()

# 测试查询
test_queries = [
    "查一下技术部的员工",
    "什么是RAG",
    "列出当前目录的文件",
    "今天天气怎么样"
]

for q in test_queries:
    result = agent.chat_sync(q)
    print(f"Q: {q}")
    print(f"Intent: {result['intent']}, Tool: {result['tool']}")
    print(f"Answer: {result['answer'][:150]}...")
    print()