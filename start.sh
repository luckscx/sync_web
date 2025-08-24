#!/bin/bash

echo "🚀 启动Sync Web应用..."
echo "📱 多端数据同步平台"
echo "=" * 50

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 检查依赖是否安装
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 安装依赖..."
    uv pip install -r requirements.txt
fi

# 启动应用
echo "🌐 启动Flask应用..."
echo "=" * 50

python run.py
