# AgentX 企业智能助手

基于 Agent + MCP 的企业级智能助手，支持任务规划、工具调用和智能问答。

## 项目描述

AgentX 是一个企业级 AI Agent 框架，核心架构：
- **Agent 核心**：任务规划、意图识别、工具选择
- **MCP 工具层**：知识库搜索、数据库查询、文件操作、API调用
- **执行层**：工具调度、结果整合、响应生成

## 技术栈

| 技术 | 说明 |
|-----|------|
| FastMCP | MCP框架（70% MCP服务器使用） |
| SQLite | 员工数据库 |
| LangChain | RAG知识库集成 |
| OpenAI/DeepSeek | LLM调用 |
| FastAPI | API服务 |

## 快速开始

```bash
cd AgentX
pip install -r requirements.txt

# 启动API服务
python agent.py serve

# 测试
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "查询技术部的员工"}'
```

## MCP 工具（FastMCP实现）

根据官方文档，使用 `@mcp.tool()` 装饰器自动生成工具schema：

```python
from fastmcp import FastMCP
mcp = FastMCP("AgentX Tools")

@mcp.tool()
def search_employees(keyword: str = "", department: str = "") -> str:
    """搜索员工信息
    
    Args:
        keyword: 搜索关键词
        department: 部门
    """
    # 工具实现
    return "员工列表..."
```

### 已注册工具

| 工具 | 功能 | 参数 |
|-----|------|------|
| search_knowledgebase | RAG知识库搜索 | query |
| search_employees | 员工搜索 | keyword, department |
| get_employee_info | 员工详情 | employee_id |
| list_departments | 部门列表 | - |
| list_files | 列出文件 | directory |
| read_file | 读取文件 | path |
| call_api | API代理 | url, method, data |

### Resources

| 资源 | 说明 |
|-----|------|
| company://stats | 公司统计 |

## 项目结构

```
AgentX/
├── agent.py        # Agent核心
├── mcp_tools.py   # FastMCP工具层
├── config.py      # 配置
├── requirements.txt
└── data/         # 数据目录
```

## 对比参考项目

| 特性 | GitHub AgentX | 本项目 |
|-----|-------------|--------|
| 规模 | 完整平台 | 轻量实现 |
| MCP实现 | 集成 | FastMCP |
| Token | 完整 | 简化版 |

## 参考资料

- [FastMCP官方](https://gofastmcp.com)
- [FastMCP GitHub](https://github.com/prefecthq/fastmcp)
- [MCP文档](https://modelcontextprotocol.info)