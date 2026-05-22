# AgentX Dockerfile - 企业AI助手私有化部署
# 多阶段构建，最终镜像 ~300MB

# ========== 构建阶段 ==========
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装构建依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ========== 运行阶段 ==========
FROM python:3.11-slim

LABEL maintainer="AgentX"
LABEL description="企业智能助手 - 私有化部署"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash agentx

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /install /usr/local

# 复制应用代码
COPY . .

# 创建数据目录并设置权限
RUN mkdir -p /app/data /app/logs \
    && chown -R agentx:agentx /app

USER agentx

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

# 默认使用 gunicorn 生产服务器（也可用 uvicorn）
CMD ["gunicorn", "-c", "gunicorn.conf.py", "agent:app"]
