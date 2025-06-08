#!/usr/bin/env python3
"""
文件批量处理工具
支持文件重命名、复制、移动、转换等批量操作
"""

import os
import shutil
import re
from typing import List, Dict, Optional, Callable
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

console = Console()

class FileProcessor:
    """文件批量处理器"""
    
    def __init__(self):
        self.processed_files = []
        self.errors = []
        self.operations_log = []
    
    def batch_rename(self, directory: str, pattern: str, replacement: str, 
                    preview: bool = False) -> Dict[str, List[str]]:
        """批量重命名文件
        
        Args:
            directory: 目标目录
            pattern: 正则表达式模式
            replacement: 替换字符串
            preview: 是否只预览，不实际执行
        """
        if not os.path.exists(directory):
            self.errors.append(f"目录不存在: {directory}")
            return {'renamed': [], 'errors': self.errors}
        
        renamed_files = []
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            self.errors.append(f"正则表达式错误: {e}")
            return {'renamed': [], 'errors': self.errors}
        
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("处理文件...", total=len(files))
            
            for filename in files:
                progress.update(task, description=f"处理: {filename}")
                
                if regex.search(filename):
                    new_name = regex.sub(replacement, filename)
                    old_path = os.path.join(directory, filename)
                    new_path = os.path.join(directory, new_name)
                    
                    if preview:
                        renamed_files.append(f"{filename} -> {new_name}")
                        self.operations_log.append(f"预览: {filename} -> {new_name}")
                    else:
                        try:
                            if os.path.exists(new_path):
                                self.errors.append(f"目标文件已存在: {new_name}")
                            else:
                                os.rename(old_path, new_path)
                                renamed_files.append(f"{filename} -> {new_name}")
                                self.processed_files.append(new_path)
                                self.operations_log.append(f"重命名: {filename} -> {new_name}")
                        except Exception as e:
                            self.errors.append(f"重命名失败 {filename}: {e}")
                
                progress.advance(task)
        
        return {'renamed': renamed_files, 'errors': self.errors}
    
    def batch_copy(self, source_dir: str, target_dir: str, 
                  file_pattern: str = "*", overwrite: bool = False) -> Dict[str, int]:
        """批量复制文件"""
        if not os.path.exists(source_dir):
            self.errors.append(f"源目录不存在: {source_dir}")
            return {'copied': 0, 'failed': 0}
        
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取匹配的文件
        source_path = Path(source_dir)
        files = list(source_path.glob(file_pattern))
        files = [f for f in files if f.is_file()]
        
        copied_count = 0
        failed_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("复制文件...", total=len(files))
            
            for file_path in files:
                progress.update(task, description=f"复制: {file_path.name}")
                
                target_file = os.path.join(target_dir, file_path.name)
                
                try:
                    if os.path.exists(target_file) and not overwrite:
                        self.errors.append(f"目标文件已存在: {file_path.name}")
                        failed_count += 1
                    else:
                        shutil.copy2(str(file_path), target_file)
                        copied_count += 1
                        self.processed_files.append(target_file)
                        self.operations_log.append(f"复制: {file_path} -> {target_file}")
                
                except Exception as e:
                    self.errors.append(f"复制失败 {file_path.name}: {e}")
                    failed_count += 1
                
                progress.advance(task)
        
        return {'copied': copied_count, 'failed': failed_count}
    
    def batch_move(self, source_dir: str, target_dir: str, 
                  file_pattern: str = "*", overwrite: bool = False) -> Dict[str, int]:
        """批量移动文件"""
        if not os.path.exists(source_dir):
            self.errors.append(f"源目录不存在: {source_dir}")
            return {'moved': 0, 'failed': 0}
        
        # 创建目标目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取匹配的文件
        source_path = Path(source_dir)
        files = list(source_path.glob(file_pattern))
        files = [f for f in files if f.is_file()]
        
        moved_count = 0
        failed_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("移动文件...", total=len(files))
            
            for file_path in files:
                progress.update(task, description=f"移动: {file_path.name}")
                
                target_file = os.path.join(target_dir, file_path.name)
                
                try:
                    if os.path.exists(target_file) and not overwrite:
                        self.errors.append(f"目标文件已存在: {file_path.name}")
                        failed_count += 1
                    else:
                        shutil.move(str(file_path), target_file)
                        moved_count += 1
                        self.processed_files.append(target_file)
                        self.operations_log.append(f"移动: {file_path} -> {target_file}")
                
                except Exception as e:
                    self.errors.append(f"移动失败 {file_path.name}: {e}")
                    failed_count += 1
                
                progress.advance(task)
        
        return {'moved': moved_count, 'failed': failed_count}
    
    def organize_by_extension(self, directory: str, create_folders: bool = True) -> Dict[str, int]:
        """按文件扩展名组织文件"""
        if not os.path.exists(directory):
            self.errors.append(f"目录不存在: {directory}")
            return {'organized': 0, 'failed': 0}
        
        files = [f for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f))]
        
        organized_count = 0
        failed_count = 0
        
        # 按扩展名分组
        extension_groups = {}
        for filename in files:
            ext = Path(filename).suffix.lower()
            if not ext:
                ext = 'no_extension'
            else:
                ext = ext[1:]  # 移除点号
            
            if ext not in extension_groups:
                extension_groups[ext] = []
            extension_groups[ext].append(filename)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("组织文件...", total=len(files))
            
            for ext, file_list in extension_groups.items():
                if create_folders:
                    ext_dir = os.path.join(directory, ext)
                    os.makedirs(ext_dir, exist_ok=True)
                
                for filename in file_list:
                    progress.update(task, description=f"组织: {filename}")
                    
                    source_path = os.path.join(directory, filename)
                    target_path = os.path.join(directory, ext, filename) if create_folders else source_path
                    
                    try:
                        if create_folders and source_path != target_path:
                            shutil.move(source_path, target_path)
                            organized_count += 1
                            self.processed_files.append(target_path)
                            self.operations_log.append(f"组织: {filename} -> {ext}/")
                    
                    except Exception as e:
                        self.errors.append(f"组织失败 {filename}: {e}")
                        failed_count += 1
                    
                    progress.advance(task)
        
        return {'organized': organized_count, 'failed': failed_count}
    
    def clean_empty_dirs(self, directory: str) -> int:
        """清理空目录"""
        removed_count = 0
        
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # 目录为空
                        os.rmdir(dir_path)
                        removed_count += 1
                        self.operations_log.append(f"删除空目录: {dir_path}")
                except Exception as e:
                    self.errors.append(f"删除目录失败 {dir_path}: {e}")
        
        return removed_count
    
    def get_report(self) -> Dict:
        """获取处理报告"""
        return {
            'processed_files': self.processed_files,
            'errors': self.errors,
            'operations_log': self.operations_log,
            'total_processed': len(self.processed_files),
            'total_errors': len(self.errors)
        }
    
    def print_report(self):
        """打印处理报告"""
        report = self.get_report()
        
        console.print("\n📊 [bold]文件处理报告[/bold]")
        
        # 创建统计表格
        table = Table(title="处理统计")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="green")
        
        table.add_row("处理成功", str(report['total_processed']))
        table.add_row("处理失败", str(report['total_errors']))
        table.add_row("总操作数", str(len(report['operations_log'])))
        
        console.print(table)
        
        if report['operations_log']:
            console.print("\n📝 [bold green]操作日志:[/bold green]")
            for log in report['operations_log'][-10:]:  # 显示最后10条
                console.print(f"  • {log}")
            
            if len(report['operations_log']) > 10:
                console.print(f"  ... 还有 {len(report['operations_log']) - 10} 条记录")
        
        if report['errors']:
            console.print("\n⚠️ [bold red]错误信息:[/bold red]")
            for error in report['errors']:
                console.print(f"  • {error}")


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="文件批量处理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 重命名命令
    rename_parser = subparsers.add_parser('rename', help='批量重命名文件')
    rename_parser.add_argument('directory', help='目标目录')
    rename_parser.add_argument('pattern', help='正则表达式模式')
    rename_parser.add_argument('replacement', help='替换字符串')
    rename_parser.add_argument('--preview', action='store_true', help='预览模式')
    
    # 复制命令
    copy_parser = subparsers.add_parser('copy', help='批量复制文件')
    copy_parser.add_argument('source', help='源目录')
    copy_parser.add_argument('target', help='目标目录')
    copy_parser.add_argument('--pattern', default='*', help='文件模式')
    copy_parser.add_argument('--overwrite', action='store_true', help='覆盖已存在文件')
    
    # 移动命令
    move_parser = subparsers.add_parser('move', help='批量移动文件')
    move_parser.add_argument('source', help='源目录')
    move_parser.add_argument('target', help='目标目录')
    move_parser.add_argument('--pattern', default='*', help='文件模式')
    move_parser.add_argument('--overwrite', action='store_true', help='覆盖已存在文件')
    
    # 组织命令
    organize_parser = subparsers.add_parser('organize', help='按扩展名组织文件')
    organize_parser.add_argument('directory', help='目标目录')
    organize_parser.add_argument('--no-folders', action='store_true', help='不创建文件夹')
    
    # 清理命令
    clean_parser = subparsers.add_parser('clean', help='清理空目录')
    clean_parser.add_argument('directory', help='目标目录')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    processor = FileProcessor()
    
    try:
        if args.command == 'rename':
            console.print(f"🔄 批量重命名: {args.directory}")
            result = processor.batch_rename(args.directory, args.pattern, 
                                          args.replacement, args.preview)
            
            if args.preview:
                console.print("\n👀 [bold yellow]预览结果:[/bold yellow]")
                for rename in result['renamed']:
                    console.print(f"  • {rename}")
            else:
                console.print(f"✅ 重命名完成: {len(result['renamed'])} 个文件")
        
        elif args.command == 'copy':
            console.print(f"📋 批量复制: {args.source} -> {args.target}")
            result = processor.batch_copy(args.source, args.target, 
                                        args.pattern, args.overwrite)
            console.print(f"✅ 复制完成: {result['copied']} 个文件")
        
        elif args.command == 'move':
            console.print(f"📦 批量移动: {args.source} -> {args.target}")
            result = processor.batch_move(args.source, args.target, 
                                        args.pattern, args.overwrite)
            console.print(f"✅ 移动完成: {result['moved']} 个文件")
        
        elif args.command == 'organize':
            console.print(f"🗂️ 组织文件: {args.directory}")
            result = processor.organize_by_extension(args.directory, 
                                                   not args.no_folders)
            console.print(f"✅ 组织完成: {result['organized']} 个文件")
        
        elif args.command == 'clean':
            console.print(f"🧹 清理空目录: {args.directory}")
            removed = processor.clean_empty_dirs(args.directory)
            console.print(f"✅ 清理完成: 删除了 {removed} 个空目录")
        
        # 显示报告
        processor.print_report()
        
        return 0
    
    except Exception as e:
        console.print(f"❌ 执行失败: {e}", style="red")
        return 1


if __name__ == "__main__":
    exit(main())