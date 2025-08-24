#!/bin/bash

# 配置变量
APP_NAME="sync_web"
APP_PORT=8000
WORKERS=4
PID_FILE="./${APP_NAME}.pid"
LOG_FILE="./logs/${APP_NAME}.log"
ACCESS_LOG_FILE="./logs/${APP_NAME}_access.log"

echo "🚀 启动Sync Web应用..."
echo "📱 多端数据同步平台"
echo "=================================================="

# 创建日志目录
mkdir -p logs

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 检查依赖是否安装
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "📥 安装生产环境依赖..."
    uv pip install -r requirements.txt
fi

# 检查应用是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  应用已经在运行 (PID: $PID)"
        echo "💡 如需重启，请先运行: ./stop.sh"
        exit 1
    else
        echo "🧹 清理过期的PID文件..."
        rm -f "$PID_FILE"
    fi
fi

# 启动Gunicorn服务
echo "🌐 启动Gunicorn WSGI服务器..."
echo "📍 端口: $APP_PORT"
echo "👥 工作进程: $WORKERS"
echo "📝 日志文件: $LOG_FILE"
echo "📊 访问日志: $ACCESS_LOG_FILE"
echo "=================================================="

# 启动Gunicorn
gunicorn \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:$APP_PORT \
    --workers $WORKERS \
    --pid $PID_FILE \
    --log-file $LOG_FILE \
    --access-logfile $ACCESS_LOG_FILE \
    --daemon \
    app:app

# 等待服务启动
sleep 3

# 检查服务状态
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 应用启动成功！"
        echo "🆔 进程ID: $PID"
        echo "🌐 访问地址: http://localhost:$APP_PORT"
        echo "📝 查看日志: tail -f $LOG_FILE"
        echo "📊 查看访问日志: tail -f $ACCESS_LOG_FILE"
        echo "🛑 停止服务: ./stop.sh"
        echo "🔄 重启服务: ./restart.sh"
    else
        echo "❌ 应用启动失败，请检查日志文件"
        exit 1
    fi
else
    echo "❌ 应用启动失败，PID文件未创建"
    exit 1
fi
