"""
OpenDevinAI520 Web界面
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config import load_config
from src.tools import ToolManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'opendevinai520-web-interface'

# 初始化
logger = setup_logger("WebApp")
config = load_config()
tool_manager = ToolManager(config)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', tools=tool_manager.list_tools())

@app.route('/api/tools')
def api_tools():
    """获取工具列表API"""
    tools = []
    for tool_name in tool_manager.list_tools():
        tool = tool_manager.get_tool(tool_name)
        if tool:
            tools.append({
                'name': tool_name,
                'description': tool.get_description()
            })
    return jsonify(tools)

@app.route('/api/execute', methods=['POST'])
def api_execute():
    """执行工具API"""
    try:
        data = request.get_json()
        tool_name = data.get('tool')
        action = data.get('action')
        args = data.get('args', [])
        
        if not tool_name or not action:
            return jsonify({'error': '缺少必要参数'}), 400
        
        tool = tool_manager.get_tool(tool_name)
        if not tool:
            return jsonify({'error': f'工具 {tool_name} 不存在'}), 404
        
        result = tool.execute(action, args)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        logger.error(f"执行工具失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tools/<tool_name>')
def tool_page(tool_name):
    """工具页面"""
    tool = tool_manager.get_tool(tool_name)
    if not tool:
        return "工具不存在", 404
    
    return render_template('tool.html', 
                         tool_name=tool_name, 
                         tool_description=tool.get_description())

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """文件上传API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        # 保存文件到临时目录
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'path': str(file_path)
        })
    
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def api_download(filename):
    """文件下载API"""
    try:
        file_path = Path('downloads') / filename
        if not file_path.exists():
            return "文件不存在", 404
        
        return send_file(str(file_path), as_attachment=True)
    
    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        return "下载失败", 500

@app.route('/docs')
def docs():
    """文档页面"""
    return render_template('docs.html')

@app.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 创建必要的目录
    Path('uploads').mkdir(exist_ok=True)
    Path('downloads').mkdir(exist_ok=True)
    
    # 启动Web服务器
    logger.info("🌐 启动Web界面...")
    app.run(host='0.0.0.0', port=12000, debug=config.get('app', {}).get('debug', False))