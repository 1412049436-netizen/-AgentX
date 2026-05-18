"""测试AgentX - 直接测试核心功能"""

# 导入
from agent import AgentX

agent = AgentX()

print("=" * 50)
print("AgentX 功能测试")
print("=" * 50)

# 测试查询
tests = [
    ("查一下技术部的员工", "query_employee"),
    ("什么是RAG", "query_knowledge"),
    ("列出当前目录的文件", "file_operation"),
]

for msg, expected_intent in tests:
    result = agent.chat_sync(msg)
    print(f"\nQ: {msg}")
    print(f"  Intent: {result['intent']} (期望: {expected_intent})")
    print(f"  Tool: {result['tool']}")
    print(f"  Answer: {result['answer'][:100]}...")

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)