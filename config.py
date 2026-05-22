"""
AgentX 配置 - 支持本地/云 LLM 双模式
"""

import os

# Agent配置
AGENT_NAME = "AgentX"
AGENT_VERSION = "1.0.0"

# 服务配置
HOST = "0.0.0.0"
PORT = int(os.getenv("AGENTX_PORT", "8001"))

# 日志
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# RAG知识库路径（容器内可配置）
RAG_PATH = os.getenv("RAG_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "RAG"))

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

# LLM配置 - 支持 ollama / deepseek / qwen / openai
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deepseek")

# DeepSeek（云端）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Qwen（云端）
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-turbo"

# OpenAI（云端）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o-mini"

# Ollama（本地私有化部署）
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# 默认模型（根据LLM_PROVIDER自动选择）
DEFAULT_MODEL = {
    "deepseek": DEEPSEEK_MODEL,
    "qwen": QWEN_MODEL,
    "openai": OPENAI_MODEL,
    "ollama": OLLAMA_MODEL,
}.get(LLM_PROVIDER, DEEPSEEK_MODEL)

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
