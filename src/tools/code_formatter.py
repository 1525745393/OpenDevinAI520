#!/usr/bin/env python3
"""
代码格式化工具
支持多种编程语言的代码格式化
"""

import os
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class CodeFormatter:
    """代码格式化器"""
    
    SUPPORTED_LANGUAGES = {
        'python': {
            'extensions': ['.py'],
            'formatter': 'black',
            'install_cmd': 'pip install black',
            'format_cmd': 'black {file}'
        },
        'javascript': {
            'extensions': ['.js', '.jsx'],
            'formatter': 'prettier',
            'install_cmd': 'npm install -g prettier',
            'format_cmd': 'prettier --write {file}'
        },
        'typescript': {
            'extensions': ['.ts', '.tsx'],
            'formatter': 'prettier',
            'install_cmd': 'npm install -g prettier',
            'format_cmd': 'prettier --write {file}'
        },
        'json': {
            'extensions': ['.json'],
            'formatter': 'built-in',
            'install_cmd': None,
            'format_cmd': None
        },
        'css': {
            'extensions': ['.css', '.scss', '.sass'],
            'formatter': 'prettier',
            'install_cmd': 'npm install -g prettier',
            'format_cmd': 'prettier --write {file}'
        }
    }
    
    def __init__(self):
        self.formatted_files = []
        self.errors = []
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """检测文件的编程语言"""
        ext = Path(file_path).suffix.lower()
        for lang, config in self.SUPPORTED_LANGUAGES.items():
            if ext in config['extensions']:
                return lang
        return None
    
    def format_json(self, file_path: str) -> bool:
        """格式化JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.errors.append(f"格式化 {file_path} 失败: {e}")
            return False
    
    def format_file(self, file_path: str) -> bool:
        """格式化单个文件"""
        if not os.path.exists(file_path):
            self.errors.append(f"文件不存在: {file_path}")
            return False
        
        language = self.detect_language(file_path)
        if not language:
            self.errors.append(f"不支持的文件类型: {file_path}")
            return False
        
        config = self.SUPPORTED_LANGUAGES[language]
        
        # 特殊处理JSON文件
        if language == 'json':
            return self.format_json(file_path)
        
        # 检查格式化工具是否可用
        formatter = config['formatter']
        if not self._check_formatter_available(formatter):
            self.errors.append(f"格式化工具 {formatter} 不可用，请先安装: {config['install_cmd']}")
            return False
        
        # 执行格式化命令
        try:
            cmd = config['format_cmd'].format(file=file_path)
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                self.formatted_files.append(file_path)
                return True
            else:
                self.errors.append(f"格式化 {file_path} 失败: {result.stderr}")
                return False
        
        except Exception as e:
            self.errors.append(f"执行格式化命令失败: {e}")
            return False
    
    def format_directory(self, directory: str, recursive: bool = True) -> Dict[str, int]:
        """格式化目录中的所有支持的文件"""
        if not os.path.exists(directory):
            console.print(f"❌ 目录不存在: {directory}", style="red")
            return {'success': 0, 'failed': 0}
        
        files_to_format = []
        
        # 收集需要格式化的文件
        if recursive:
            for root, dirs, files in os.walk(directory):
                # 跳过常见的忽略目录
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.detect_language(file_path):
                        files_to_format.append(file_path)
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and self.detect_language(file_path):
                    files_to_format.append(file_path)
        
        if not files_to_format:
            console.print("📝 没有找到支持的文件", style="yellow")
            return {'success': 0, 'failed': 0}
        
        # 格式化文件
        success_count = 0
        failed_count = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("正在格式化文件...", total=len(files_to_format))
            
            for file_path in files_to_format:
                progress.update(task, description=f"格式化: {os.path.basename(file_path)}")
                
                if self.format_file(file_path):
                    success_count += 1
                else:
                    failed_count += 1
                
                progress.advance(task)
        
        return {'success': success_count, 'failed': failed_count}
    
    def _check_formatter_available(self, formatter: str) -> bool:
        """检查格式化工具是否可用"""
        try:
            subprocess.run([formatter, '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_report(self) -> Dict:
        """获取格式化报告"""
        return {
            'formatted_files': self.formatted_files,
            'errors': self.errors,
            'total_formatted': len(self.formatted_files),
            'total_errors': len(self.errors)
        }
    
    def print_report(self):
        """打印格式化报告"""
        report = self.get_report()
        
        console.print("\n📊 [bold]格式化报告[/bold]")
        console.print(f"✅ 成功格式化: {report['total_formatted']} 个文件")
        console.print(f"❌ 失败: {report['total_errors']} 个文件")
        
        if report['formatted_files']:
            console.print("\n📝 [bold green]已格式化的文件:[/bold green]")
            for file in report['formatted_files']:
                console.print(f"  • {file}")
        
        if report['errors']:
            console.print("\n⚠️ [bold red]错误信息:[/bold red]")
            for error in report['errors']:
                console.print(f"  • {error}")


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="代码格式化工具")
    parser.add_argument('path', help='要格式化的文件或目录路径')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归处理子目录')
    parser.add_argument('--report', action='store_true', help='显示详细报告')
    
    args = parser.parse_args()
    
    formatter = CodeFormatter()
    
    if os.path.isfile(args.path):
        # 格式化单个文件
        console.print(f"🔧 格式化文件: {args.path}")
        success = formatter.format_file(args.path)
        
        if success:
            console.print("✅ 格式化完成", style="green")
        else:
            console.print("❌ 格式化失败", style="red")
    
    elif os.path.isdir(args.path):
        # 格式化目录
        console.print(f"🔧 格式化目录: {args.path}")
        result = formatter.format_directory(args.path, args.recursive)
        
        console.print(f"✅ 完成! 成功: {result['success']}, 失败: {result['failed']}")
    
    else:
        console.print(f"❌ 路径不存在: {args.path}", style="red")
        return 1
    
    if args.report:
        formatter.print_report()
    
    return 0


if __name__ == "__main__":
    exit(main())