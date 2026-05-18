"""
MCP 工具封装 - 使用FastMCP
基于 FastMCP 官方文档的最佳实践
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# FastMCP
from fastmcp import FastMCP

# 添加RAG路径
RAG_PATH = Path(__file__).parent.parent / "RAG"
if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

# 创建MCP服务器
mcp = FastMCP("AgentX Tools")

# 数据库路径
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "enterprise.db"


# ============= 数据库初始化 =============
def init_db():
    """初始化员工数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT,
        position TEXT,
        email TEXT,
        phone TEXT,
        created_at TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT
    )''')
    
    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0] == 0:
        employees = [
            ('001', '张三', '技术部', 'AI工程师', 'zhangsan@company.com', '13800001111'),
            ('002', '李四', '产品部', '产品经理', 'lisi@company.com', '13800002222'),
            ('003', '王五', '技术部', '后端工程师', 'wangwu@company.com', '13800003333'),
            ('004', '赵六', '运营部', '运营专员', 'zhaoliu@company.com', '13800004444'),
            ('005', '钱七', '技术部', '前端工程师', 'qianqi@company.com', '13800005555'),
        ]
        c.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, datetime('now'))", employees)
        
        c.execute("INSERT OR IGNORE INTO departments (name, description) VALUES ('技术部', '负责技术研发')")
        c.execute("INSERT OR IGNORE INTO departments (name, description) VALUES ('产品部', '负责产品规划')")
        c.execute("INSERT OR IGNORE INTO departments (name, description) VALUES ('运营部', '负责运营推广')")
    
    conn.commit()
    conn.close()


# ============== Tools ==============

# 工具1: 搜索RAG知识库
@mcp.tool()
def search_knowledgebase(query: str) -> str:
    """搜索企业知识库中的文档
    
    Args:
        query: 搜索关键词
        
    Returns:
        搜索结果文本
    """
    try:
        from src.retrieval import get_context
        context = get_context(query, k=3)
        if context:
            return f"搜索 '{query}' 的结果：\n\n{context}"
        return f"未找到与 '{query}' 相关的内容"
    except Exception as e:
        return f"知识库搜索失败: {str(e)}"


# 工具2: 搜索员工
@mcp.tool()
def search_employees(keyword: str = "", department: str = "") -> str:
    """搜索员工信息
    
    Args:
        keyword: 搜索关键词（姓名、部门、职位）
        department: 直接指定部门
        
    Returns:
        员工列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if department:
        c.execute("SELECT * FROM employees WHERE department = ?", (department,))
    elif keyword:
        c.execute("""SELECT * FROM employees 
                    WHERE name LIKE ? OR department LIKE ? OR position LIKE ?
                    LIMIT 10""", 
                 (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    else:
        c.execute("SELECT * FROM employees LIMIT 10")
    
    results = c.fetchall()
    conn.close()
    
    if not results:
        return "未找到员工"
    
    lines = ["员工列表："]
    for r in results:
        lines.append(f"- {r['name']} | {r['department']} | {r['position']} | {r['email']}")
    
    return "\n".join(lines)


# 工具3: 获取员工详情
@mcp.tool()
def get_employee_info(employee_id: str) -> dict:
    """获取特定员工的详细信息
    
    Args:
        employee_id: 员工ID
        
    Returns:
        员工详情字典
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "name": row["name"],
            "department": row["department"],
            "position": row["position"],
            "email": row["email"],
            "phone": row["phone"]
        }
    return {"error": "员工不存在"}


# 工具4: 列出部门
@mcp.tool()
def list_departments() -> str:
    """列出所有部门
    
    Returns:
        部门列表
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, description FROM departments")
    depts = c.fetchall()
    conn.close()
    
    if not depts:
        return "暂无部门"
    
    lines = ["部门列表："]
    for d in depts:
        lines.append(f"- {d[0]}: {d[1] if d[1] else ''}")
    return "\n".join(lines)


# 工具5: 列出文件
@mcp.tool()
def list_files(directory: str = ".") -> str:
    """列出目录下的文件
    
    Args:
        directory: 目录路径
        
    Returns:
        文件列表
    """
    p = Path(directory)
    if not p.exists():
        return f"目录不存在: {directory}"
    
    files = list(p.iterdir())[:15]
    if not files:
        return "目录为空"
    
    lines = [f"目录 {directory}:"]
    for f in files:
        lines.append(f"  {'[DIR]' if f.is_dir() else '[FILE]'} {f.name}")
    return "\n".join(lines)


# 工具6: 读取文件
@mcp.tool()
def read_file(path: str) -> str:
    """读取文件内容
    
    Args:
        path: 文件路径
        
    Returns:
        文件内容
    """
    p = Path(path)
    if not p.exists():
        return f"文件不存在: {path}"
    
    try:
        content = p.read_text(encoding='utf-8')
        if len(content) > 2000:
            content = content[:2000] + "\n... (截断)"
        return f"文件: {path}\n\n{content}"
    except Exception as e:
        return f"读取失败: {str(e)}"


# 工具7: 调用API
@mcp.tool()
def call_api(url: str, method: str = "GET", data: dict = None) -> str:
    """调用外部REST API
    
    Args:
        url: API地址
        method: HTTP方法 (GET/POST)
        data: POST请求时的数据
        
    Returns:
        API响应
    """
    import requests
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        elif method == "POST":
            r = requests.post(url, json=data, timeout=10)
        else:
            return f"不支持: {method}"
        
        return f"状态: {r.status_code}\n响应: {r.text[:500]}"
    except Exception as e:
        return f"请求失败: {str(e)}"


# ============== 启动 ==============
if __name__ == "__main__":
    init_db()
    print("AgentX MCP Server 启动中...")
    mcp.run(transport="stdio")