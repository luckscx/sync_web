from flask import Flask, request, jsonify, render_template, send_file, make_response
from flask_cors import CORS
import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sync_secret_key_2024')
CORS(app)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3', 'zip', 'rar'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 存储数据的简单文件（生产环境建议使用数据库）
DATA_FILE = 'sync_data.json'
COOKIE_PASSWORD = os.getenv('COOKIE_PASSWORD', 'sync123')  # 从环境变量读取密码，默认值sync123

def load_data():
    """加载同步数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'texts': [], 'files': []}

def save_data(data):
    """保存同步数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_password(password):
    """验证密码"""
    return password == COOKIE_PASSWORD

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """登录验证"""
    data = request.get_json()
    password = data.get('password', '')
    
    if verify_password(password):
        # 创建3个月有效期的cookie
        response = make_response(jsonify({'success': True, 'message': '登录成功'}))
        expires = datetime.now() + timedelta(days=90)
        response.set_cookie('sync_auth', 'authenticated', expires=expires, httponly=True, secure=False)
        return response
    
    return jsonify({'success': False, 'message': '密码错误'}), 401

@app.route('/api/check-auth')
def check_auth():
    """检查认证状态"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie == 'authenticated':
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False}), 401

@app.route('/api/sync-text', methods=['POST'])
def sync_text():
    """同步文本"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'message': '文本不能为空'}), 400
    
    sync_data = load_data()
    
    # 获取UserAgent信息
    user_agent = request.headers.get('User-Agent', '')
    
    # 添加新文本到开头
    new_text_item = {
        'id': str(uuid.uuid4()),
        'content': text,
        'type': 'text',
        'timestamp': datetime.now().isoformat(),
        'size': len(text.encode('utf-8')),
        'user_agent': user_agent
    }
    
    sync_data['texts'].insert(0, new_text_item)
    
    # 保持最多5个文本
    sync_data['texts'] = sync_data['texts'][:5]
    
    save_data(sync_data)
    
    return jsonify({'success': True, 'message': '文本同步成功'})

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """上传文件"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{file_id}.{file_ext}"
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(file_path)
        
        sync_data = load_data()
        
        # 获取UserAgent信息
        user_agent = request.headers.get('User-Agent', '')
        
        # 添加新文件记录到开头
        new_file_item = {
            'id': file_id,
            'original_name': filename,
            'filename': new_filename,
            'type': 'file',
            'timestamp': datetime.now().isoformat(),
            'size': os.path.getsize(file_path),
            'extension': file_ext,
            'user_agent': user_agent
        }
        
        sync_data['files'].insert(0, new_file_item)
        
        # 保持最多5个文件
        sync_data['files'] = sync_data['files'][:5]
        
        save_data(sync_data)
        
        return jsonify({'success': True, 'message': '文件上传成功'})
    
    return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

@app.route('/api/history')
def get_history():
    """获取历史记录"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    sync_data = load_data()
    
    # 合并文本和文件记录，按时间排序
    all_items = sync_data['texts'] + sync_data['files']
    all_items.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 返回前5个
    return jsonify({'success': True, 'data': all_items[:5]})

@app.route('/api/download/<file_id>')
def download_file(file_id):
    """下载文件"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    sync_data = load_data()
    
    # 查找文件记录
    file_item = None
    for item in sync_data['files']:
        if item['id'] == file_id:
            file_item = item
            break
    
    if not file_item:
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_item['filename'])
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=file_item['original_name'])

@app.route('/api/logout')
def logout():
    """登出"""
    response = make_response(jsonify({'success': True, 'message': '已登出'}))
    response.delete_cookie('sync_auth')
    return response

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host=host, port=port)
