"""
文件批量处理工具
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.utils.logger import setup_logger
from src.utils.file_utils import FileUtils

class FileProcessor:
    """文件批量处理工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化文件处理工具
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = setup_logger("FileProcessor")
        self.file_utils = FileUtils()
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "文件批量处理工具 - 支持批量重命名、复制、移动等操作"
    
    def execute(self, action: str, args: List[str]) -> Optional[str]:
        """
        执行工具操作
        
        Args:
            action: 操作名称
            args: 参数列表
            
        Returns:
            Optional[str]: 执行结果
        """
        if action == "batch_rename":
            return self._batch_rename(args)
        elif action == "batch_copy":
            return self._batch_copy(args)
        elif action == "batch_move":
            return self._batch_move(args)
        elif action == "find_duplicates":
            return self._find_duplicates(args)
        elif action == "organize":
            return self._organize_files(args)
        elif action == "cleanup":
            return self._cleanup_files(args)
        elif action == "help":
            return self._show_help()
        else:
            return f"未知操作: {action}"
    
    def _batch_rename(self, args: List[str]) -> str:
        """
        批量重命名文件
        
        Args:
            args: 参数列表 [pattern, replacement, directory]
            
        Returns:
            str: 重命名结果
        """
        if len(args) < 2:
            return "参数不足。用法: batch_rename <模式> <替换> [目录]"
        
        pattern = args[0]
        replacement = args[1]
        directory = Path(args[2]) if len(args) > 2 else Path.cwd()
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        renamed_count = 0
        error_count = 0
        
        try:
            # 查找匹配的文件
            files = list(directory.glob(pattern))
            
            for file_path in files:
                if file_path.is_file():
                    try:
                        # 生成新文件名
                        old_name = file_path.name
                        new_name = re.sub(pattern.replace('*', '.*'), replacement, old_name)
                        
                        if new_name != old_name:
                            new_path = file_path.parent / new_name
                            
                            # 检查目标文件是否已存在
                            if new_path.exists():
                                self.logger.warning(f"目标文件已存在，跳过: {new_path}")
                                error_count += 1
                                continue
                            
                            file_path.rename(new_path)
                            self.logger.info(f"重命名: {old_name} -> {new_name}")
                            renamed_count += 1
                    
                    except Exception as e:
                        self.logger.error(f"重命名失败 {file_path}: {e}")
                        error_count += 1
            
            return f"批量重命名完成: {renamed_count} 个文件成功, {error_count} 个文件失败"
        
        except Exception as e:
            return f"批量重命名失败: {e}"
    
    def _batch_copy(self, args: List[str]) -> str:
        """
        批量复制文件
        
        Args:
            args: 参数列表 [source_pattern, destination]
            
        Returns:
            str: 复制结果
        """
        if len(args) < 2:
            return "参数不足。用法: batch_copy <源模式> <目标目录>"
        
        source_pattern = args[0]
        destination = Path(args[1])
        
        # 确保目标目录存在
        self.file_utils.ensure_dir(destination)
        
        copied_count = 0
        error_count = 0
        
        try:
            # 查找匹配的文件
            source_dir = Path.cwd()
            files = list(source_dir.glob(source_pattern))
            
            for file_path in files:
                if file_path.is_file():
                    try:
                        dest_path = destination / file_path.name
                        
                        if self.file_utils.copy_file(file_path, dest_path):
                            self.logger.info(f"复制: {file_path} -> {dest_path}")
                            copied_count += 1
                        else:
                            error_count += 1
                    
                    except Exception as e:
                        self.logger.error(f"复制失败 {file_path}: {e}")
                        error_count += 1
            
            return f"批量复制完成: {copied_count} 个文件成功, {error_count} 个文件失败"
        
        except Exception as e:
            return f"批量复制失败: {e}"
    
    def _batch_move(self, args: List[str]) -> str:
        """
        批量移动文件
        
        Args:
            args: 参数列表 [source_pattern, destination]
            
        Returns:
            str: 移动结果
        """
        if len(args) < 2:
            return "参数不足。用法: batch_move <源模式> <目标目录>"
        
        source_pattern = args[0]
        destination = Path(args[1])
        
        # 确保目标目录存在
        self.file_utils.ensure_dir(destination)
        
        moved_count = 0
        error_count = 0
        
        try:
            # 查找匹配的文件
            source_dir = Path.cwd()
            files = list(source_dir.glob(source_pattern))
            
            for file_path in files:
                if file_path.is_file():
                    try:
                        dest_path = destination / file_path.name
                        
                        if self.file_utils.move_file(file_path, dest_path):
                            self.logger.info(f"移动: {file_path} -> {dest_path}")
                            moved_count += 1
                        else:
                            error_count += 1
                    
                    except Exception as e:
                        self.logger.error(f"移动失败 {file_path}: {e}")
                        error_count += 1
            
            return f"批量移动完成: {moved_count} 个文件成功, {error_count} 个文件失败"
        
        except Exception as e:
            return f"批量移动失败: {e}"
    
    def _find_duplicates(self, args: List[str]) -> str:
        """
        查找重复文件
        
        Args:
            args: 参数列表 [directory]
            
        Returns:
            str: 查找结果
        """
        directory = Path(args[0]) if args else Path.cwd()
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        try:
            # 按文件大小分组
            size_groups = {}
            files = list(directory.rglob("*"))
            
            for file_path in files:
                if file_path.is_file():
                    size = self.file_utils.get_file_size(file_path)
                    if size not in size_groups:
                        size_groups[size] = []
                    size_groups[size].append(file_path)
            
            # 查找可能的重复文件（相同大小）
            potential_duplicates = {size: files for size, files in size_groups.items() if len(files) > 1}
            
            # 使用哈希值确认重复文件
            duplicates = {}
            for size, files in potential_duplicates.items():
                hash_groups = {}
                for file_path in files:
                    try:
                        file_hash = self.file_utils.get_file_hash(file_path)
                        if file_hash not in hash_groups:
                            hash_groups[file_hash] = []
                        hash_groups[file_hash].append(file_path)
                    except Exception as e:
                        self.logger.error(f"计算文件哈希失败 {file_path}: {e}")
                
                # 收集真正的重复文件
                for file_hash, duplicate_files in hash_groups.items():
                    if len(duplicate_files) > 1:
                        duplicates[file_hash] = duplicate_files
            
            if duplicates:
                result = f"找到 {len(duplicates)} 组重复文件:\n"
                for i, (file_hash, files) in enumerate(duplicates.items(), 1):
                    result += f"\n组 {i} (哈希: {file_hash[:8]}...):\n"
                    for file_path in files:
                        size = self.file_utils.format_file_size(self.file_utils.get_file_size(file_path))
                        result += f"  - {file_path} ({size})\n"
                return result
            else:
                return "未找到重复文件"
        
        except Exception as e:
            return f"查找重复文件失败: {e}"
    
    def _organize_files(self, args: List[str]) -> str:
        """
        按类型组织文件
        
        Args:
            args: 参数列表 [directory]
            
        Returns:
            str: 组织结果
        """
        directory = Path(args[0]) if args else Path.cwd()
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        # 文件类型映射
        type_mapping = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c'],
        }
        
        organized_count = 0
        error_count = 0
        
        try:
            files = [f for f in directory.iterdir() if f.is_file()]
            
            for file_path in files:
                try:
                    suffix = file_path.suffix.lower()
                    target_folder = None
                    
                    # 确定目标文件夹
                    for folder_name, extensions in type_mapping.items():
                        if suffix in extensions:
                            target_folder = folder_name
                            break
                    
                    if not target_folder:
                        target_folder = 'others'
                    
                    # 创建目标目录
                    target_dir = directory / target_folder
                    self.file_utils.ensure_dir(target_dir)
                    
                    # 移动文件
                    target_path = target_dir / file_path.name
                    if self.file_utils.move_file(file_path, target_path):
                        self.logger.info(f"组织文件: {file_path.name} -> {target_folder}/")
                        organized_count += 1
                    else:
                        error_count += 1
                
                except Exception as e:
                    self.logger.error(f"组织文件失败 {file_path}: {e}")
                    error_count += 1
            
            return f"文件组织完成: {organized_count} 个文件成功, {error_count} 个文件失败"
        
        except Exception as e:
            return f"文件组织失败: {e}"
    
    def _cleanup_files(self, args: List[str]) -> str:
        """
        清理临时文件
        
        Args:
            args: 参数列表 [directory]
            
        Returns:
            str: 清理结果
        """
        directory = Path(args[0]) if args else Path.cwd()
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        # 临时文件模式
        temp_patterns = [
            '*.tmp', '*.temp', '*.bak', '*.backup',
            '*.log', '*.cache', '*~', '.DS_Store',
            'Thumbs.db', '*.pyc', '__pycache__'
        ]
        
        cleaned_count = 0
        error_count = 0
        
        try:
            for pattern in temp_patterns:
                files = list(directory.rglob(pattern))
                
                for file_path in files:
                    try:
                        if file_path.is_file():
                            file_path.unlink()
                            self.logger.info(f"删除临时文件: {file_path}")
                            cleaned_count += 1
                        elif file_path.is_dir() and pattern == '__pycache__':
                            shutil.rmtree(file_path)
                            self.logger.info(f"删除临时目录: {file_path}")
                            cleaned_count += 1
                    
                    except Exception as e:
                        self.logger.error(f"删除失败 {file_path}: {e}")
                        error_count += 1
            
            return f"清理完成: {cleaned_count} 个文件/目录成功, {error_count} 个失败"
        
        except Exception as e:
            return f"清理失败: {e}"
    
    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
文件批量处理工具帮助:

操作:
  batch_rename <模式> <替换> [目录]  - 批量重命名文件
  batch_copy <源模式> <目标目录>     - 批量复制文件
  batch_move <源模式> <目标目录>     - 批量移动文件
  find_duplicates [目录]           - 查找重复文件
  organize [目录]                  - 按类型组织文件
  cleanup [目录]                   - 清理临时文件
  help                            - 显示此帮助信息

示例:
  file_processor batch_rename "*.txt" "backup_*.txt"
  file_processor batch_copy "*.jpg" ./images/
  file_processor find_duplicates ./downloads/
  file_processor organize ./messy_folder/
  file_processor cleanup ./temp/
"""