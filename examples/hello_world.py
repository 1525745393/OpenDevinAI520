#!/usr/bin/env python3
"""
OpenDevinAI520 示例程序 - Hello World
展示如何使用 OpenDevinAI520 平台
"""

from rich.console import Console
from rich.panel import Panel

def main():
    """主函数"""
    console = Console()
    
    # 创建欢迎消息
    welcome_text = """
🎉 欢迎使用 OpenDevinAI520！

这是一个简单的示例程序，展示了如何：
• 使用 Rich 库创建美观的控制台输出
• 构建模块化的Python应用程序
• 遵循项目的代码规范

人人为我，我为人人 - 让我们一起构建更好的开发工具生态！
    """
    
    # 显示面板
    panel = Panel(
        welcome_text.strip(),
        title="🚀 OpenDevinAI520 示例",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print(panel)
    
    # 显示一些基本信息
    console.print("\n📋 [bold]项目信息:[/bold]")
    console.print("• 项目名称: OpenDevinAI520")
    console.print("• 版本: 1.0.0")
    console.print("• 许可证: MIT")
    console.print("• 仓库: https://github.com/1525745393/OpenDevinAI520")
    
    console.print("\n✨ [bold cyan]感谢您的关注和支持！[/bold cyan]")

if __name__ == "__main__":
    main()