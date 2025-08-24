#!/usr/bin/env python3
"""
Gunicorn配置文件 - 生产环境
"""

import multiprocessing
import os

# 服务器配置
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# 超时配置
timeout = 30
keepalive = 2
graceful_timeout = 30

# 进程配置
preload_app = True
daemon = False  # 在start.sh中设置为True

# 日志配置
accesslog = "./logs/sync_web_access.log"
errorlog = "./logs/sync_web.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 性能配置
# worker_tmp_dir = "/dev/shm"  # Linux系统使用内存文件系统
max_requests_jitter = 100

# 环境变量
raw_env = [
    "FLASK_ENV=production",
    "FLASK_DEBUG=0",
]

# 钩子函数
def on_starting(server):
    """服务器启动时的回调"""
    server.log.info("🚀 Sync Web应用正在启动...")

def on_reload(server):
    """重载时的回调"""
    server.log.info("🔄 应用正在重载...")

def worker_int(worker):
    """工作进程中断时的回调"""
    worker.log.info("⚠️  工作进程被中断")

def pre_fork(server, worker):
    """fork工作进程前的回调"""
    server.log.info(f"👥 准备fork工作进程 {worker.pid}")

def post_fork(server, worker):
    """fork工作进程后的回调"""
    server.log.info(f"✅ 工作进程 {worker.pid} 已启动")

def post_worker_init(worker):
    """工作进程初始化后的回调"""
    worker.log.info(f"🔧 工作进程 {worker.pid} 初始化完成")

def worker_abort(worker):
    """工作进程异常退出时的回调"""
    worker.log.info(f"❌ 工作进程 {worker.pid} 异常退出")

def on_exit(server):
    """服务器退出时的回调"""
    server.log.info("👋 Sync Web应用正在退出...")
