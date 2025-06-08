"""
文件操作工具模块
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Generator
import hashlib

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """
        确保目录存在，如果不存在则创建
        
        Args:
            path: 目录路径
            
        Returns:
            Path: 目录路径
        """
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法 (md5, sha1, sha256)
            
        Returns:
            str: 文件哈希值
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def find_files(directory: Path, pattern: str = "*", recursive: bool = True) -> List[Path]:
        """
        查找文件
        
        Args:
            directory: 搜索目录
            pattern: 文件模式
            recursive: 是否递归搜索
            
        Returns:
            List[Path]: 匹配的文件列表
        """
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    
    @staticmethod
    def copy_file(src: Path, dst: Path, overwrite: bool = False) -> bool:
        """
        复制文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            bool: 是否成功复制
        """
        try:
            if dst.exists() and not overwrite:
                return False
            
            FileUtils.ensure_dir(dst.parent)
            shutil.copy2(src, dst)
            return True
        except Exception:
            return False
    
    @staticmethod
    def move_file(src: Path, dst: Path, overwrite: bool = False) -> bool:
        """
        移动文件
        
        Args:
            src: 源文件路径
            dst: 目标文件路径
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            bool: 是否成功移动
        """
        try:
            if dst.exists() and not overwrite:
                return False
            
            FileUtils.ensure_dir(dst.parent)
            shutil.move(str(src), str(dst))
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        return file_path.stat().st_size
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小
        """
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def read_file_lines(file_path: Path, encoding: str = "utf-8") -> Generator[str, None, None]:
        """
        逐行读取文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Yields:
            str: 文件行内容
        """
        with open(file_path, 'r', encoding=encoding) as f:
            for line in f:
                yield line.rstrip('\n\r')
    
    @staticmethod
    def write_file(file_path: Path, content: str, encoding: str = "utf-8", append: bool = False) -> bool:
        """
        写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码
            append: 是否追加模式
            
        Returns:
            bool: 是否成功写入
        """
        try:
            FileUtils.ensure_dir(file_path.parent)
            mode = 'a' if append else 'w'
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
            
            return True
        except Exception:
            return False