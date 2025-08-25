from flask import Flask, request, jsonify, render_template, send_file, make_response, redirect
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
            data = json.load(f)
            # 确保新字段存在
            if 'urls' not in data:
                data['urls'] = []
            if 'url_counter' not in data:
                data['url_counter'] = 0
            return data
    return {'texts': [], 'files': [], 'urls': [], 'url_counter': 0}

def save_data(data):
    """保存同步数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_short_code(counter):
    """生成短链接代码"""
    # 使用hashlib生成8位短码
    hash_obj = hashlib.md5(str(counter).encode())
    return hash_obj.hexdigest()[:8]

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

@app.route('/api/shorten-url', methods=['POST'])
def shorten_url():
    """缩短URL"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    data = request.get_json()
    long_url = data.get('url', '').strip()
    
    if not long_url:
        return jsonify({'success': False, 'message': 'URL不能为空'}), 400
    
    # 简单的URL格式验证
    if not long_url.startswith(('http://', 'https://')):
        return jsonify({'success': False, 'message': '请输入有效的HTTP或HTTPS URL'}), 400
    
    sync_data = load_data()
    
    # 检查URL是否已经存在
    for url_item in sync_data['urls']:
        if url_item['long_url'] == long_url:
            short_code = url_item['short_code']
            short_url = f"{request.host_url.rstrip('/')}/s/{short_code}"
            return jsonify({
                'success': True, 
                'message': 'URL已存在',
                'short_url': short_url,
                'short_code': short_code
            })
    
    # 生成新的短链接
    sync_data['url_counter'] += 1
    short_code = generate_short_code(sync_data['url_counter'])
    
    # 获取UserAgent信息
    user_agent = request.headers.get('User-Agent', '')
    
    # 添加新URL记录到开头
    new_url_item = {
        'id': str(uuid.uuid4()),
        'long_url': long_url,
        'short_code': short_code,
        'type': 'url',
        'timestamp': datetime.now().isoformat(),
        'clicks': 0,
        'user_agent': user_agent
    }
    
    sync_data['urls'].insert(0, new_url_item)
    
    # 保持最多20个URL
    sync_data['urls'] = sync_data['urls'][:20]
    
    save_data(sync_data)
    
    short_url = f"{request.host_url.rstrip('/')}/s/{short_code}"
    
    return jsonify({
        'success': True, 
        'message': 'URL缩短成功',
        'short_url': short_url,
        'short_code': short_code
    })

@app.route('/s/<short_code>')
def redirect_short_url(short_code):
    """短链接重定向"""
    sync_data = load_data()
    
    # 查找短链接
    url_item = None
    for item in sync_data['urls']:
        if item['short_code'] == short_code:
            url_item = item
            break
    
    if not url_item:
        return jsonify({'success': False, 'message': '短链接不存在'}), 404
    
    # 增加点击次数
    url_item['clicks'] += 1
    save_data(sync_data)
    
    # 301重定向到长URL
    return redirect(url_item['long_url'], code=301)

@app.route('/api/url-history')
def get_url_history():
    """获取URL历史记录"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    sync_data = load_data()
    
    # 返回所有URL记录，按时间排序
    urls = sorted(sync_data['urls'], key=lambda x: x['timestamp'], reverse=True)
    
    # 为每个URL添加完整的短链接
    for url_item in urls:
        url_item['short_url'] = f"{request.host_url.rstrip('/')}/s/{url_item['short_code']}"
    
    return jsonify({'success': True, 'data': urls})

@app.route('/api/delete-url/<url_id>', methods=['DELETE'])
def delete_url(url_id):
    """删除URL"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    sync_data = load_data()
    
    # 查找并删除URL
    for i, url_item in enumerate(sync_data['urls']):
        if url_item['id'] == url_id:
            del sync_data['urls'][i]
            save_data(sync_data)
            return jsonify({'success': True, 'message': 'URL删除成功'})
    
    return jsonify({'success': False, 'message': 'URL不存在'}), 404

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

@app.route('/api/clear-history', methods=['POST', 'DELETE'])
def clear_history():
    """清空所有历史记录"""
    auth_cookie = request.cookies.get('sync_auth')
    if auth_cookie != 'authenticated':
        return jsonify({'success': False, 'message': '未认证'}), 401
    
    try:
        # 清空数据
        sync_data = {'texts': [], 'files': [], 'urls': [], 'url_counter': 0}
        save_data(sync_data)
        
        # 清空上传的文件
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({'success': True, 'message': '历史记录已清空'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'清空失败: {str(e)}'}), 500

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
