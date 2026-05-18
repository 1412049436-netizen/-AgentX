"""
AgentX 配置
"""

import os

# Agent配置
AGENT_NAME = "AgentX"
AGENT_VERSION = "1.0.0"

# 服务配置
HOST = "0.0.0.0"
PORT = 8001

# 日志
LOG_LEVEL = "INFO"

# RAG知识库路径
RAG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "RAG")

# MCP工具配置
TOOLS = {
    "knowledgebase": {
        "enabled": True,
        "description": "搜索企业知识库"
    },
    "employees": {
        "enabled": True,
        "description": "查询员工信息"
    },
    "files": {
        "enabled": True,
        "description": "文件操作"
    },
    "api": {
        "enabled": True,
        "description": "API代理"
    }
}

# LLM配置 - 使用DeepSeek（免费额度）
LLM_PROVIDER = "deepseek"  # deepseek / qwen / openai
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 模型
DEFAULT_MODEL = "deepseek-chat" if LLM_PROVIDER == "deepseek" else "qwen-turbo"

# 意图分类
INTENT_PATTERNS = {
    "query_employee": ["查员工", "查询员工", "员工信息", "谁", "有人叫", "技术部", "产品部", "运营部", "销售部", "财务部"],
    "query_knowledge": ["是什么", "怎么", "如何", "文档", "知识库", "什么"],
    "file_operation": ["读取", "写入", "文件", "看看", "列出", "目录"],
    "general": []
}

# 工具映射
TOOL_MAPPING = {
    "query_employee": "search_employees",
    "query_knowledge": "search_knowledgebase",
    "file_operation": "list_files"
}