"""
工具管理器
"""

import sys
from typing import Dict, Any, List
from src.utils.logger import setup_logger
from .code_formatter import CodeFormatter
from .file_processor import FileProcessor
from .api_tester import ApiTester
from .data_converter import DataConverter
from .media_renamer import MediaRenamer

class ToolManager:
    """工具管理器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化工具管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = setup_logger("ToolManager")
        self.tools = {}
        self._init_tools()
    
    def _init_tools(self):
        """初始化工具"""
        enabled_tools = self.config.get("tools", {}).get("enabled", [])
        
        # 可用工具映射
        available_tools = {
            "code_formatter": CodeFormatter,
            "file_processor": FileProcessor,
            "api_tester": ApiTester,
            "data_converter": DataConverter,
            "media_renamer": MediaRenamer
        }
        
        # 初始化启用的工具
        for tool_name in enabled_tools:
            if tool_name in available_tools:
                try:
                    self.tools[tool_name] = available_tools[tool_name](self.config)
                    self.logger.info(f"✅ 工具 {tool_name} 初始化成功")
                except Exception as e:
                    self.logger.error(f"❌ 工具 {tool_name} 初始化失败: {e}")
    
    def get_tool(self, tool_name: str):
        """
        获取工具实例
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例或None
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        获取可用工具列表
        
        Returns:
            List[str]: 工具名称列表
        """
        return list(self.tools.keys())
    
    def start_cli(self):
        """启动命令行界面"""
        self.logger.info("🎯 启动交互式命令行界面")
        
        while True:
            try:
                command = input("\n🛠️  OpenDevinAI520> ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    print("👋 再见！")
                    break
                
                if command.lower() in ['help', 'h']:
                    self._show_help()
                    continue
                
                if command.lower() in ['list', 'ls']:
                    self._list_tools()
                    continue
                
                # 解析命令
                parts = command.split()
                if len(parts) < 2:
                    print("❌ 命令格式错误。使用 'help' 查看帮助。")
                    continue
                
                tool_name = parts[0]
                action = parts[1]
                args = parts[2:] if len(parts) > 2 else []
                
                self._execute_tool_command(tool_name, action, args)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                self.logger.error(f"❌ 命令执行出错: {e}")
                print(f"❌ 执行出错: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
📖 OpenDevinAI520 帮助信息

🔧 基本命令:
  help, h          - 显示此帮助信息
  list, ls         - 列出所有可用工具
  exit, quit, q    - 退出程序

🛠️  工具命令格式:
  <工具名> <操作> [参数...]

📋 可用工具:
"""
        print(help_text)
        
        for tool_name, tool_instance in self.tools.items():
            print(f"  {tool_name:<15} - {tool_instance.get_description()}")
            
        print("\n💡 示例:")
        print("  code_formatter format example.py")
        print("  file_processor batch_rename *.txt")
        print("  api_tester test http://api.example.com")
        print("  data_converter json_to_csv data.json")
    
    def _list_tools(self):
        """列出所有工具"""
        print("\n🛠️  可用工具:")
        for i, (tool_name, tool_instance) in enumerate(self.tools.items(), 1):
            status = "✅ 已启用"
            print(f"  {i}. {tool_name:<15} - {tool_instance.get_description()} ({status})")
        
        if not self.tools:
            print("  暂无可用工具")
    
    def _execute_tool_command(self, tool_name: str, action: str, args: List[str]):
        """
        执行工具命令
        
        Args:
            tool_name: 工具名称
            action: 操作名称
            args: 参数列表
        """
        tool = self.get_tool(tool_name)
        if not tool:
            print(f"❌ 工具 '{tool_name}' 不存在或未启用")
            return
        
        try:
            result = tool.execute(action, args)
            if result:
                print(f"✅ 操作完成: {result}")
            else:
                print("❌ 操作失败")
        except Exception as e:
            self.logger.error(f"❌ 工具 {tool_name} 执行失败: {e}")
            print(f"❌ 执行失败: {e}")