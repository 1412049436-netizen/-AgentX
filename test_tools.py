"""测试AgentX - 简化版"""

import sys

# 强制不使用API key
sys.argv.append("--test")

from mcp_tools import TOOLS, execute_tool, list_departments, search_employees

# 初始化
from mcp_tools import init_db
init_db()

print("=" * 50)
print("AgentX 工具测试")
print("=" * 50)

# 1. 列出部门
print("\n1. 部门列表:")
result = list_departments()
print(f"   {result}")

# 2. 员工搜索
print("\n2. 员工搜索(技术部):")
result = search_employees(department="技术部")
print(f"   {result}")

# 3. 员工搜索(关键词)
print("\n3. 员工搜索(张三):")
result = search_employees(keyword="张三")
print(f"   {result}")

# 4. 文件列表
print("\n4. 文件列表:")
from mcp_tools import list_files
result = list_files(".")
print(f"   {result[:200]}")

print("\n" + "=" * 50)
print("工具测试通过!")
print("=" * 50)