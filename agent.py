"""
AgentX 核心
任务规划、意图识别、工具选择、响应生成
"""

import os
import re
import json
import asyncio
from typing import Dict, Any, List, Optional
from openai import OpenAI

from config import (
    LLM_PROVIDER, DEEPSEEK_API_KEY, QWEN_API_KEY, OPENAI_API_KEY,
    DEEPSEEK_BASE_URL, QWEN_BASE_URL, OPENAI_BASE_URL,
    OLLAMA_HOST, OLLAMA_MODEL, DEFAULT_MODEL,
    INTENT_PATTERNS, TOOL_MAPPING
)
from mcp_tools import init_db


# 工具注册表
TOOLS = {
    "search_knowledgebase": {
        "description": "搜索企业知识库中的文档",
        "params": {"query": "搜索关键词"}
    },
    "search_employees": {
        "description": "搜索员工信息，支持按姓名、部门",
        "params": {"keyword": "搜索关键词(可选)", "department": "部门(可选)"}
    },
    "get_employee_info": {
        "description": "获取特定员工的详细信息",
        "params": {"employee_id": "员工ID"}
    },
    "list_departments": {
        "description": "列出所有部门",
        "params": {}
    },
    "list_files": {
        "description": "列出目录下的文件",
        "params": {"directory": "目录路径"}
    },
    "read_file": {
        "description": "读取文件内容",
        "params": {"path": "文件路径"}
    },
    "call_api": {
        "description": "调用外部API",
        "params": {"url": "API地址", "method": "GET/POST", "data": "请求数据"}
    }
}


class AgentX:
    """企业智能助手 Agent"""
    
    def __init__(self):
        self.name = "AgentX"
        self.tools = TOOLS
        self._init_llm()
        init_db()
        print(f"{self.name} 初始化完成 [LLM: {LLM_PROVIDER}, Model: {self.model if self.client else 'rule-only'}]")
    
    def _init_llm(self):
        """初始化LLM客户端（支持Ollama本地/DeepSeek/Qwen/OpenAI）"""
        if LLM_PROVIDER == "ollama":
            base_url = f"{OLLAMA_HOST}/v1"
            api_key = "ollama"  # Ollama 不需要真 key，但 OpenAI 客户端要求非空
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            self.model = OLLAMA_MODEL
            print(f"LLM初始化: Ollama @ {OLLAMA_HOST} | Model: {self.model}")
            return

        if LLM_PROVIDER == "deepseek":
            api_key = DEEPSEEK_API_KEY
            base_url = DEEPSEEK_BASE_URL
        elif LLM_PROVIDER == "qwen":
            api_key = QWEN_API_KEY or os.getenv("DASHSCOPE_API_KEY", "")
            base_url = QWEN_BASE_URL
        elif LLM_PROVIDER == "openai":
            api_key = OPENAI_API_KEY
            base_url = OPENAI_BASE_URL
        else:
            api_key = DEEPSEEK_API_KEY
            base_url = DEEPSEEK_BASE_URL

        if not api_key:
            print("警告: 未设置API Key，使用规则匹配模式（无LLM）")
            self.client = None
            self.model = "rule-only"
            return
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = DEFAULT_MODEL
        print(f"LLM初始化: {LLM_PROVIDER} | Model: {self.model}")
    
    def _classify_intent(self, message: str) -> str:
        """意图分类（规则匹配）"""
        message_lower = message.lower()
        
        for intent, patterns in INTENT_PATTERNS.items():
            for p in patterns:
                if p in message_lower:
                    return intent
        
        return "general"
    
    def _classify_intent_llm(self, message: str) -> str:
        """意图分类（LLM）"""
        if not self.client:
            return self._classify_intent(message)
        
        prompt = f"""请判断用户意图，只返回意图类型：
- query_employee: 查询员工
- query_knowledge: 查询知识/文档
- file_operation: 文件操作
- general: 一般问答

用户消息: {message}
意图:"""
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=50
            )
            intent = resp.choices[0].message.content.strip()
            return intent if intent in TOOL_MAPPING else "general"
        except Exception as e:
            print(f"意图分类失败: {e}")
            return self._classify_intent(message)
    
    def _extract_params(self, intent: str, message: str) -> Dict[str, Any]:
        """提取参数"""
        params = {}
        
        if intent == "query_employee":
            depts = ["技术部", "产品部", "运营部", "销售部", "财务部"]
            for d in depts:
                if d in message:
                    params["department"] = d
                    break
        
        elif intent == "query_knowledge":
            params["query"] = message.strip()
            for w in ["是什么", "怎么", "如何", "什么是", "?", "？"]:
                params["query"] = params["query"].replace(w, "").strip()
            if not params["query"]:
                params["query"] = message
        
        return params
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """执行工具"""
        try:
            if tool_name == "search_employees":
                from mcp_tools import search_employees
                return search_employees(**params)
            elif tool_name == "search_knowledgebase":
                from mcp_tools import search_knowledgebase
                return search_knowledgebase(**params)
            elif tool_name == "list_departments":
                from mcp_tools import list_departments
                return list_departments()
            elif tool_name == "list_files":
                from mcp_tools import list_files
                return list_files(**params)
            elif tool_name == "get_employee_info":
                from mcp_tools import get_employee_info
                return get_employee_info(**params)
            elif tool_name == "call_api":
                from mcp_tools import call_api
                return call_api(**params)
            else:
                return f"未知工具: {tool_name}"
        except Exception as e:
            return f"工具执行失败: {str(e)}"
    
    def _build_context(self, intent: str, message: str, tool_result: str) -> str:
        """构建上下文用于生成回答"""
        context = f"""用户问题: {message}
工具结果: {tool_result}

请根据工具结果用自然语言回答用户问题。"""
        return context
    
    def _generate_response(self, message: str, context: str) -> str:
        """生成自然语言回答"""
        if not self.client:
            return context
        
        prompt = f"""你是一个企业智能助手，请根据给定的上下文回答用户问题。
如果上下文已经回答了用户问题，直接返回结果，不要重复"根据上下文"。

用户原始问题: {message}

上下文:
{context}

回答:"""
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"生成回答失败: {e}")
            return context
    
    async def chat(self, message: str) -> Dict[str, Any]:
        """处理对话"""
        intent = self._classify_intent_llm(message)
        tool_name = TOOL_MAPPING.get(intent)
        
        if not tool_name:
            if self.client:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": message}],
                    temperature=0.7
                )
                answer = resp.choices[0].message.content.strip()
            else:
                answer = "抱歉，我理解不了这个问题。建议问我：查员工、查知识、查文件等。"
            
            return {
                "intent": "general",
                "answer": answer,
                "tool": None,
                "result": None
            }
        
        params = self._extract_params(intent, message)
        tool_result = self._execute_tool(tool_name, params)
        context = self._build_context(intent, message, tool_result)
        answer = self._generate_response(message, context)
        
        return {
            "intent": intent,
            "tool": tool_name,
            "params": params,
            "tool_result": tool_result,
            "answer": answer
        }
    
    def chat_sync(self, message: str) -> Dict[str, Any]:
        """同步版本"""
        return asyncio.run(self.chat(message))


# 全局Agent实例
_agent: Optional[AgentX] = None


def get_agent() -> AgentX:
    """获取Agent实例"""
    global _agent
    if _agent is None:
        _agent = AgentX()
    return _agent


# ========== API ==========
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AgentX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    intent: str
    tool: Optional[str] = None
    tool_result: Optional[str] = None


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """对话接口"""
    agent = get_agent()
    result = await agent.chat(req.message)
    
    return ChatResponse(
        answer=result["answer"],
        intent=result["intent"],
        tool=result["tool"],
        tool_result=result.get("tool_result")
    )


@app.get("/tools")
async def list_tools():
    """工具列表"""
    return {
        name: {
            "description": info["description"],
            "params": info["params"]
        }
        for name, info in TOOLS.items()
    }


@app.get("/health")
async def health():
    """健康检查"""
    from config import LLM_PROVIDER, DEFAULT_MODEL
    return {
        "status": "ok",
        "agent": "AgentX",
        "llm_provider": LLM_PROVIDER,
        "model": DEFAULT_MODEL
    }


# ========== CLI ==========
import click


@click.group()
def cli():
    """AgentX 企业智能助手"""
    pass


@cli.command()
def serve():
    """启动API服务"""
    import uvicorn
    from config import HOST, PORT
    
    print(f"AgentX 服务启动: http://{HOST}:{PORT}")
    print(f"LLM Provider: {LLM_PROVIDER}")
    uvicorn.run(app, host=HOST, port=PORT)


@cli.command()
@click.argument("message")
def ask(message: str):
    """命令行对话"""
    agent = get_agent()
    result = agent.chat_sync(message)
    print(f"\n[{result['intent']}] {result['answer']}")


if __name__ == "__main__":
    cli()
