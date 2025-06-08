#!/usr/bin/env python3
"""
文件批量处理工具测试
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.file_processor import FileProcessor


class TestFileProcessor(unittest.TestCase):
    """文件批量处理工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = FileProcessor()
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.test_files = [
            'old_file1.txt',
            'old_file2.txt', 
            'old_file3.txt',
            'document.pdf',
            'image.jpg',
            'script.py'
        ]
        
        for filename in self.test_files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f'Content of {filename}')
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_batch_rename_preview(self):
        """测试批量重命名预览模式"""
        result = self.processor.batch_rename(
            self.temp_dir, 
            'old_', 
            'new_', 
            preview=True
        )
        
        self.assertIn('renamed', result)
        self.assertIn('errors', result)
        self.assertTrue(len(result['renamed']) > 0)
        
        # 预览模式不应该实际重命名文件
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'old_file1.txt')))
    
    def test_batch_rename_execute(self):
        """测试批量重命名执行"""
        result = self.processor.batch_rename(
            self.temp_dir, 
            'old_', 
            'new_'
        )
        
        self.assertIn('renamed', result)
        self.assertTrue(len(result['renamed']) > 0)
        
        # 验证文件已被重命名
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'new_file1.txt')))
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, 'old_file1.txt')))
    
    def test_batch_copy(self):
        """测试批量复制"""
        target_dir = os.path.join(self.temp_dir, 'target')
        
        result = self.processor.batch_copy(
            self.temp_dir,
            target_dir,
            '*.txt'
        )
        
        self.assertIn('copied', result)
        self.assertIn('failed', result)
        self.assertTrue(result['copied'] > 0)
        
        # 验证文件已被复制
        self.assertTrue(os.path.exists(os.path.join(target_dir, 'old_file1.txt')))
    
    def test_batch_move(self):
        """测试批量移动"""
        target_dir = os.path.join(self.temp_dir, 'target')
        
        result = self.processor.batch_move(
            self.temp_dir,
            target_dir,
            '*.pdf'
        )
        
        self.assertIn('moved', result)
        self.assertIn('failed', result)
        
        # 验证文件已被移动
        self.assertTrue(os.path.exists(os.path.join(target_dir, 'document.pdf')))
        self.assertFalse(os.path.exists(os.path.join(self.temp_dir, 'document.pdf')))
    
    def test_organize_by_extension(self):
        """测试按扩展名组织文件"""
        result = self.processor.organize_by_extension(self.temp_dir)
        
        self.assertIn('organized', result)
        self.assertIn('failed', result)
        
        # 验证目录结构
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'txt')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'pdf')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'jpg')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'py')))
    
    def test_clean_empty_dirs(self):
        """测试清理空目录"""
        # 创建空目录
        empty_dir1 = os.path.join(self.temp_dir, 'empty1')
        empty_dir2 = os.path.join(self.temp_dir, 'empty2')
        os.makedirs(empty_dir1)
        os.makedirs(empty_dir2)
        
        # 创建非空目录
        non_empty_dir = os.path.join(self.temp_dir, 'non_empty')
        os.makedirs(non_empty_dir)
        with open(os.path.join(non_empty_dir, 'file.txt'), 'w') as f:
            f.write('content')
        
        removed_count = self.processor.clean_empty_dirs(self.temp_dir)
        
        self.assertEqual(removed_count, 2)
        self.assertFalse(os.path.exists(empty_dir1))
        self.assertFalse(os.path.exists(empty_dir2))
        self.assertTrue(os.path.exists(non_empty_dir))
    
    def test_get_report(self):
        """测试获取处理报告"""
        report = self.processor.get_report()
        
        self.assertIsInstance(report, dict)
        self.assertIn('processed_files', report)
        self.assertIn('errors', report)
        self.assertIn('operations_log', report)
        self.assertIn('total_processed', report)
        self.assertIn('total_errors', report)
    
    def test_invalid_directory(self):
        """测试无效目录处理"""
        result = self.processor.batch_rename('/nonexistent/directory', 'old', 'new')
        
        self.assertIn('errors', result)
        self.assertTrue(len(result['errors']) > 0)
    
    def test_invalid_regex(self):
        """测试无效正则表达式"""
        result = self.processor.batch_rename(self.temp_dir, '[invalid', 'new')
        
        self.assertIn('errors', result)
        self.assertTrue(len(result['errors']) > 0)


if __name__ == '__main__':
    unittest.main()