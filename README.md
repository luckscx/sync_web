# Sync - 多端数据同步平台

一个简单的web应用，用于在多个设备间快速同步文本和文件数据。

## 功能特性

- 🔐 **安全认证**: 密码登录，3个月有效期cookie
- 📝 **文本同步**: 快速同步文本内容到云端
- 📁 **文件上传**: 支持多种文件格式上传
- 📋 **历史记录**: 查看最近5个同步项目
- 📱 **响应式设计**: 支持手机和电脑端访问
- 🎨 **现代UI**: 美观的渐变界面设计

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5 + CSS3 + JavaScript
- **数据存储**: JSON文件（可扩展为数据库）
- **文件上传**: 支持16MB以内文件

## 安装和运行

### 1. 安装依赖

```bash
# 使用uv安装依赖（推荐）
uv pip install -r requirements.txt

# 或者使用pip
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件来自定义配置：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

`.env` 文件配置示例：

```bash
# 服务器配置
HOST=0.0.0.0
PORT=8000

# 应用配置
SECRET_KEY=your_secret_key_here
COOKIE_PASSWORD=your_password_here

# 调试模式
DEBUG=True
```

### 3. 运行应用

```bash
# 使用run.py启动（推荐）
python run.py

# 或者直接启动app.py
python app.py
```

应用将在配置的host和port上启动（默认: `http://localhost:8000`）

### 3. 访问应用

在浏览器中打开 `http://localhost:5000`

## 使用方法

### 首次登录
1. 输入密码: `sync123`
2. 点击登录按钮
3. 系统会设置3个月有效期的cookie

### 文本同步
1. 在文本框中输入要同步的内容
2. 点击"同步文本"按钮
3. 文本将保存到云端

### 文件上传
1. 点击"选择文件"按钮选择文件
2. 支持格式: txt, pdf, doc, docx, jpg, png, gif, mp4, mp3, zip, rar
3. 点击"上传文件"按钮
4. 文件将上传到云端

### 查看历史
1. 点击"刷新历史"按钮
2. 显示最近5个同步项目
3. 文本可以点击"复制文本"
4. 文件可以点击"下载文件"

## 配置说明

### 环境变量配置（推荐）

通过 `.env` 文件配置应用参数：

```bash
# 服务器配置
HOST=0.0.0.0          # 监听地址
PORT=8000              # 监听端口
DEBUG=True             # 调试模式

# 应用配置
SECRET_KEY=your_secret_key_here    # Flask密钥
COOKIE_PASSWORD=your_password_here # 登录密码
```

### 修改密码
在 `.env` 文件中修改 `COOKIE_PASSWORD` 变量：

```bash
COOKIE_PASSWORD=your_new_password
```

### 修改端口
在 `.env` 文件中修改 `PORT` 变量：

```bash
PORT=3000
```

### 修改文件大小限制
在 `app.py` 中修改 `MAX_CONTENT_LENGTH`：

```python
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
```

### 修改支持的文件类型
在 `app.py` 中修改 `ALLOWED_EXTENSIONS`：

```python
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'}
```

## 文件结构

```
sync_web/
├── app.py              # Flask主应用
├── run.py              # 应用启动脚本
├── requirements.txt    # Python依赖
├── .env                # 环境变量配置（本地开发）
├── .env.example        # 环境变量配置模板
├── templates/          # HTML模板
│   └── index.html     # 主页面
├── uploads/           # 文件上传目录（自动创建）
├── sync_data.json     # 数据存储文件（自动创建）
└── README.md          # 项目说明
```

## 安全注意事项

- 当前使用简单密码验证，生产环境建议使用更安全的认证方式
- 数据存储在本地JSON文件中，生产环境建议使用数据库
- 文件上传目录需要适当的权限控制
- 建议在生产环境中启用HTTPS

## 扩展功能

- 添加用户注册和登录系统
- 实现数据加密存储
- 添加文件版本控制
- 实现实时同步通知
- 添加数据备份和恢复功能

## 许可证

MIT License
