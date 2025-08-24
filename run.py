#!/usr/bin/env python3
"""
Sync Web应用启动脚本
"""

import os
import sys
from dotenv import load_dotenv
from app import app

# 加载环境变量
load_dotenv()

if __name__ == '__main__':
    print("🚀 启动Sync Web应用...")
    print("📱 多端数据同步平台")
    print("=" * 50)
    
    try:
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('DEBUG', 'True').lower() == 'true'
        app.run(debug=debug, host=host, port=port)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
