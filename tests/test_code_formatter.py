#!/usr/bin/env python3
"""
代码格式化工具测试
"""

import unittest
import tempfile
import os
import json
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.code_formatter import CodeFormatter


class TestCodeFormatter(unittest.TestCase):
    """代码格式化工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.formatter = CodeFormatter()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_language_python(self):
        """测试Python文件语言检测"""
        self.assertEqual(self.formatter.detect_language('test.py'), 'python')
        self.assertEqual(self.formatter.detect_language('script.py'), 'python')
    
    def test_detect_language_javascript(self):
        """测试JavaScript文件语言检测"""
        self.assertEqual(self.formatter.detect_language('app.js'), 'javascript')
        self.assertEqual(self.formatter.detect_language('component.jsx'), 'javascript')
    
    def test_detect_language_json(self):
        """测试JSON文件语言检测"""
        self.assertEqual(self.formatter.detect_language('config.json'), 'json')
    
    def test_detect_language_unsupported(self):
        """测试不支持的文件类型"""
        self.assertIsNone(self.formatter.detect_language('readme.txt'))
        self.assertIsNone(self.formatter.detect_language('image.png'))
    
    def test_format_json_file(self):
        """测试JSON文件格式化"""
        # 创建测试JSON文件
        json_file = os.path.join(self.temp_dir, 'test.json')
        test_data = {"name": "John", "age": 30, "city": "New York"}
        
        # 写入压缩的JSON
        with open(json_file, 'w') as f:
            json.dump(test_data, f, separators=(',', ':'))
        
        # 格式化文件
        result = self.formatter.format_file(json_file)
        self.assertTrue(result)
        
        # 验证格式化结果
        with open(json_file, 'r') as f:
            content = f.read()
            self.assertIn('\n', content)  # 应该有换行符
            self.assertIn('  ', content)  # 应该有缩进
    
    def test_format_nonexistent_file(self):
        """测试格式化不存在的文件"""
        result = self.formatter.format_file('/nonexistent/file.py')
        self.assertFalse(result)
        self.assertTrue(len(self.formatter.errors) > 0)
    
    def test_format_directory(self):
        """测试目录格式化"""
        # 创建测试文件
        py_file = os.path.join(self.temp_dir, 'test.py')
        with open(py_file, 'w') as f:
            f.write('def hello():print("world")')
        
        json_file = os.path.join(self.temp_dir, 'test.json')
        with open(json_file, 'w') as f:
            json.dump({"key": "value"}, f, separators=(',', ':'))
        
        # 格式化目录
        result = self.formatter.format_directory(self.temp_dir, recursive=False)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('failed', result)
    
    def test_get_report(self):
        """测试获取报告"""
        report = self.formatter.get_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('formatted_files', report)
        self.assertIn('errors', report)
        self.assertIn('total_formatted', report)
        self.assertIn('total_errors', report)
    
    def test_supported_languages_config(self):
        """测试支持的语言配置"""
        self.assertIn('python', CodeFormatter.SUPPORTED_LANGUAGES)
        self.assertIn('javascript', CodeFormatter.SUPPORTED_LANGUAGES)
        self.assertIn('json', CodeFormatter.SUPPORTED_LANGUAGES)
        
        # 验证配置结构
        for lang, config in CodeFormatter.SUPPORTED_LANGUAGES.items():
            self.assertIn('extensions', config)
            self.assertIn('formatter', config)
            self.assertIsInstance(config['extensions'], list)


if __name__ == '__main__':
    unittest.main()