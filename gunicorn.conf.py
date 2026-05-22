# Gunicorn 生产配置
import multiprocessing

# 绑定地址
bind = "0.0.0.0:8001"

# Worker 配置
workers = int(multiprocessing.cpu_count() * 0.5) + 1
worker_class = "uvicorn.workers.UvicornWorker"

# 进程命名
proc_name = "agentx"

# 日志配置
accesslog = "/app/logs/access.log"
errorlog = "/app/logs/error.log"
loglevel = "info"

# 优雅重启
graceful_timeout = 30
timeout = 120
keepalive = 5

# 请求限制
max_requests = 10000
max_requests_jitter = 1000

# 预加载应用（减少内存占用，共享 Agent 实例需谨慎）
preload_app = True
