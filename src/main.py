#!/usr/bin/env python3
"""
OpenDevinAI520 - 实用工具开发平台
主程序入口文件

人人为我，我为人人 - 让我们一起构建更好的开发工具生态！
"""

import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def show_banner():
    """显示项目横幅"""
    banner_text = Text()
    banner_text.append("OpenDevinAI520", style="bold blue")
    banner_text.append("\n实用工具开发平台", style="cyan")
    banner_text.append("\n人人为我，我为人人", style="green")
    
    panel = Panel(
        banner_text,
        title="🚀 欢迎使用",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="OpenDevinAI520 - 实用工具开发平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --help          显示帮助信息
  python main.py --version       显示版本信息
  python main.py --list-tools    列出所有可用工具
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="OpenDevinAI520 v1.0.0"
    )
    
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="列出所有可用的工具"
    )
    
    args = parser.parse_args()
    
    show_banner()
    
    if args.list_tools:
        console.print("\n📋 [bold]可用工具列表:[/bold]")
        console.print("• 代码格式化工具 [dim](开发中)[/dim]")
        console.print("• 文件批量处理工具 [dim](开发中)[/dim]")
        console.print("• API测试工具 [dim](开发中)[/dim]")
        console.print("• 数据转换工具 [dim](开发中)[/dim]")
        console.print("• 开发环境配置工具 [dim](开发中)[/dim]")
        console.print("• 日志分析工具 [dim](开发中)[/dim]")
        console.print("\n💡 [yellow]更多工具正在开发中，敬请期待！[/yellow]")
    else:
        console.print("\n🎯 [bold]使用 --help 查看所有可用选项[/bold]")
        console.print("🔧 [bold]使用 --list-tools 查看可用工具[/bold]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n👋 [yellow]感谢使用 OpenDevinAI520！[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ [red]发生错误: {e}[/red]")
        sys.exit(1)