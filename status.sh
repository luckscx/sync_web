#!/bin/bash

# 配置变量
APP_NAME="sync_web"
PID_FILE="./${APP_NAME}.pid"
APP_PORT=8000

echo "📊 Sync Web应用状态检查"
echo "=================================================="

# 检查PID文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "🆔 PID文件: $PID_FILE"
    echo "📝 PID: $PID"
    
    # 检查进程状态
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 进程状态: 运行中"
        
        # 获取进程详细信息
        PROCESS_INFO=$(ps -p $PID -o pid,ppid,command,etime 2>/dev/null | tail -1)
        echo "📋 进程信息: $PROCESS_INFO"
        
        # 检查端口占用
        if lsof -i :$APP_PORT >/dev/null 2>&1; then
            echo "🌐 端口状态: $APP_PORT 端口正在监听"
        else
            echo "⚠️  端口状态: $APP_PORT 端口未监听"
        fi
        
        # 检查内存使用
        MEMORY_INFO=$(ps -p $PID -o rss,vsz 2>/dev/null | tail -1)
        if [ ! -z "$MEMORY_INFO" ] && [ "$MEMORY_INFO" != "RSS VSZ" ]; then
            RSS=$(echo $MEMORY_INFO | awk '{print $1}')
            VSZ=$(echo $MEMORY_INFO | awk '{print $2}')
            echo "💾 内存使用: RSS=${RSS}KB, VSZ=${VSZ}KB"
        fi
        
        # 检查日志文件
        if [ -f "./logs/${APP_NAME}.log" ]; then
            echo "📝 应用日志: ./logs/${APP_NAME}.log"
            echo "📊 访问日志: ./logs/${APP_NAME}_access.log"
        fi
        
    else
        echo "❌ 进程状态: 进程不存在"
        echo "🧹 建议清理PID文件"
    fi
else
    echo "⚠️  PID文件不存在"
    echo "📊 应用状态: 未运行"
fi

echo "=================================================="
echo "💡 管理命令:"
echo "  启动: ./start.sh"
echo "  停止: ./stop.sh"
echo "  重启: ./restart.sh"
echo "  状态: ./status.sh"
