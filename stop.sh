#!/bin/bash

# 配置变量
APP_NAME="sync_web"
PID_FILE="./${APP_NAME}.pid"

echo "🛑 停止Sync Web应用..."
echo "=================================================="

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  PID文件不存在，应用可能没有运行"
    exit 0
fi

# 读取PID
PID=$(cat "$PID_FILE")

# 检查进程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "🧹 进程不存在，清理PID文件..."
    rm -f "$PID_FILE"
    exit 0
fi

echo "🆔 停止进程 (PID: $PID)..."

# 优雅停止进程
kill -TERM $PID

# 等待进程停止
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "✅ 应用已成功停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 如果优雅停止失败，强制杀死进程
echo "⚠️  优雅停止失败，强制杀死进程..."
kill -KILL $PID

# 等待进程完全停止
sleep 2

if ! ps -p $PID > /dev/null 2>&1; then
    echo "✅ 应用已强制停止"
    rm -f "$PID_FILE"
else
    echo "❌ 无法停止应用，请手动检查进程状态"
    exit 1
fi
