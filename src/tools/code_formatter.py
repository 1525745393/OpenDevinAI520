"""
代码格式化工具
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.utils.logger import setup_logger

class CodeFormatter:
    """代码格式化工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化代码格式化工具
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = setup_logger("CodeFormatter")
        
        # 支持的文件类型和对应的格式化工具
        self.formatters = {
            '.py': self._format_python,
            '.js': self._format_javascript,
            '.ts': self._format_typescript,
            '.json': self._format_json,
            '.html': self._format_html,
            '.css': self._format_css,
            '.xml': self._format_xml
        }
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "代码格式化工具 - 支持多种编程语言的代码格式化"
    
    def execute(self, action: str, args: List[str]) -> Optional[str]:
        """
        执行工具操作
        
        Args:
            action: 操作名称
            args: 参数列表
            
        Returns:
            Optional[str]: 执行结果
        """
        if action == "format":
            return self._format_files(args)
        elif action == "check":
            return self._check_format(args)
        elif action == "help":
            return self._show_help()
        else:
            return f"未知操作: {action}"
    
    def _format_files(self, file_paths: List[str]) -> str:
        """
        格式化文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            str: 格式化结果
        """
        if not file_paths:
            return "请指定要格式化的文件"
        
        formatted_count = 0
        error_count = 0
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                error_count += 1
                continue
            
            if file_path.is_dir():
                # 递归处理目录
                for sub_file in file_path.rglob("*"):
                    if sub_file.is_file() and sub_file.suffix in self.formatters:
                        if self._format_single_file(sub_file):
                            formatted_count += 1
                        else:
                            error_count += 1
            else:
                # 处理单个文件
                if self._format_single_file(file_path):
                    formatted_count += 1
                else:
                    error_count += 1
        
        return f"格式化完成: {formatted_count} 个文件成功, {error_count} 个文件失败"
    
    def _format_single_file(self, file_path: Path) -> bool:
        """
        格式化单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            suffix = file_path.suffix.lower()
            if suffix in self.formatters:
                self.logger.info(f"格式化文件: {file_path}")
                return self.formatters[suffix](file_path)
            else:
                self.logger.warning(f"不支持的文件类型: {suffix}")
                return False
        except Exception as e:
            self.logger.error(f"格式化文件失败 {file_path}: {e}")
            return False
    
    def _format_python(self, file_path: Path) -> bool:
        """格式化Python文件"""
        try:
            # 使用black格式化（如果可用）
            result = subprocess.run(
                ["black", "--quiet", str(file_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            # 如果black不可用，使用autopep8
            try:
                result = subprocess.run(
                    ["autopep8", "--in-place", str(file_path)],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            except FileNotFoundError:
                self.logger.warning("未找到Python格式化工具 (black 或 autopep8)")
                return False
    
    def _format_javascript(self, file_path: Path) -> bool:
        """格式化JavaScript文件"""
        try:
            result = subprocess.run(
                ["prettier", "--write", str(file_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            self.logger.warning("未找到JavaScript格式化工具 (prettier)")
            return False
    
    def _format_typescript(self, file_path: Path) -> bool:
        """格式化TypeScript文件"""
        return self._format_javascript(file_path)  # 使用相同的prettier
    
    def _format_json(self, file_path: Path) -> bool:
        """格式化JSON文件"""
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"JSON格式化失败: {e}")
            return False
    
    def _format_html(self, file_path: Path) -> bool:
        """格式化HTML文件"""
        try:
            result = subprocess.run(
                ["prettier", "--write", "--parser", "html", str(file_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            self.logger.warning("未找到HTML格式化工具 (prettier)")
            return False
    
    def _format_css(self, file_path: Path) -> bool:
        """格式化CSS文件"""
        try:
            result = subprocess.run(
                ["prettier", "--write", "--parser", "css", str(file_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            self.logger.warning("未找到CSS格式化工具 (prettier)")
            return False
    
    def _format_xml(self, file_path: Path) -> bool:
        """格式化XML文件"""
        try:
            import xml.etree.ElementTree as ET
            import xml.dom.minidom as minidom
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 转换为字符串并格式化
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            formatted = reparsed.toprettyxml(indent="  ")
            
            # 移除空行
            lines = [line for line in formatted.split('\n') if line.strip()]
            formatted = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            
            return True
        except Exception as e:
            self.logger.error(f"XML格式化失败: {e}")
            return False
    
    def _check_format(self, file_paths: List[str]) -> str:
        """
        检查文件格式
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            str: 检查结果
        """
        # 这里可以实现格式检查逻辑
        return "格式检查功能待实现"
    
    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
代码格式化工具帮助:

操作:
  format <文件/目录>  - 格式化指定文件或目录中的代码
  check <文件/目录>   - 检查代码格式是否符合规范
  help               - 显示此帮助信息

支持的文件类型:
  .py    - Python (使用 black 或 autopep8)
  .js    - JavaScript (使用 prettier)
  .ts    - TypeScript (使用 prettier)
  .json  - JSON (内置格式化)
  .html  - HTML (使用 prettier)
  .css   - CSS (使用 prettier)
  .xml   - XML (内置格式化)

示例:
  code_formatter format example.py
  code_formatter format src/
  code_formatter check *.js
"""