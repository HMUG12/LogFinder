import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from dateutil.parser import parse
import zipfile
import io

app = Flask(__name__)

def search_logs_in_path(base_path, keyword=None, start_date=None, end_date=None, file_pattern='*.log'):
    """在指定路径下搜索日志文件"""
    results = []
    
    for root, dirs, files in os.walk(base_path):
        for filename in files:
            # 检查文件扩展名
            if not filename.endswith('.log'):
                continue
            
            file_path = os.path.join(root, filename)
            
            try:
                # 获取文件修改时间
                file_mtime = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(file_mtime)
                
                # 日期过滤
                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue
                
                # 文件大小
                file_size = os.path.getsize(file_path)
                
                # 读取文件内容（前几行用于预览）
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    preview = ''.join(lines[:20]) if lines else ''
                
                # 关键词搜索
                if keyword:
                    found = False
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if keyword.lower() in content.lower():
                            found = True
                    if not found:
                        continue
                
                results.append({
                    'path': file_path,
                    'filename': filename,
                    'size': file_size,
                    'modified': file_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'preview': preview[:500]
                })
            except Exception as e:
                continue
    
    # 按修改时间排序
    results.sort(key=lambda x: x['modified'], reverse=True)
    return results

@app.route('/api/search', methods=['POST'])
def search_logs():
    """搜索日志文件API"""
    data = request.json
    
    base_path = data.get('path', '')
    keyword = data.get('keyword', '')
    start_date_str = data.get('startDate', '')
    end_date_str = data.get('endDate', '')
    
    if not base_path or not os.path.isdir(base_path):
        return jsonify({'error': '无效的路径'}), 400
    
    start_date = None
    end_date = None
    
    try:
        if start_date_str:
            start_date = parse(start_date_str)
        if end_date_str:
            end_date = parse(end_date_str)
    except:
        return jsonify({'error': '无效的日期格式'}), 400
    
    results = search_logs_in_path(base_path, keyword, start_date, end_date)
    return jsonify({'results': results})

@app.route('/api/file/content', methods=['POST'])
def get_file_content():
    """获取日志文件内容"""
    data = request.json
    file_path = data.get('path', '')
    
    if not file_path or not os.path.isfile(file_path):
        return jsonify({'error': '无效的文件路径'}), 400
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return jsonify({'content': content, 'path': file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/download', methods=['POST'])
def download_file():
    """下载单个日志文件"""
    data = request.json
    file_path = data.get('path', '')
    
    if not file_path or not os.path.isfile(file_path):
        return jsonify({'error': '无效的文件路径'}), 400
    
    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/download', methods=['POST'])
def download_multiple_files():
    """批量下载日志文件"""
    data = request.json
    file_paths = data.get('paths', [])
    
    if not file_paths:
        return jsonify({'error': '请选择要下载的文件'}), 400
    
    # 创建临时zip文件
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            if os.path.isfile(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    
    zip_buffer.seek(0)
    return send_file(zip_buffer, download_name='logs.zip', as_attachment=True)

@app.route('/api/path/validate', methods=['POST'])
def validate_path():
    """验证路径是否有效"""
    data = request.json
    path = data.get('path', '')
    
    if os.path.isdir(path):
        return jsonify({'valid': True, 'exists': True})
    elif os.path.isfile(path):
        return jsonify({'valid': True, 'exists': True, 'isFile': True})
    else:
        return jsonify({'valid': False, 'exists': False})

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
