#!/usr/bin/env python3
"""
OpenDevinAI520 - 实用工具开发平台
主程序入口文件

人人为我，我为人人 - 让我们一起构建更好的开发工具生态！
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config import load_config
from src.tools import ToolManager

def main():
    """主函数"""
    logger = setup_logger()
    logger.info("🚀 OpenDevinAI520 启动中...")
    
    try:
        # 加载配置
        config = load_config()
        logger.info("✅ 配置加载成功")
        
        # 初始化工具管理器
        tool_manager = ToolManager(config)
        logger.info("✅ 工具管理器初始化成功")
        
        # 显示欢迎信息
        print_welcome()
        
        # 启动交互式命令行界面
        tool_manager.start_cli()
        
    except KeyboardInterrupt:
        logger.info("👋 用户中断，程序退出")
    except Exception as e:
        logger.error(f"❌ 程序运行出错: {e}")
        sys.exit(1)

def print_welcome():
    """打印欢迎信息"""
    welcome_text = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    OpenDevinAI520                            ║
    ║                  实用工具开发平台                              ║
    ║                                                              ║
    ║              人人为我，我为人人                                ║
    ║          让我们一起构建更好的开发工具生态！                      ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🛠️  可用工具:
    - 代码格式化工具
    - 文件批量处理工具
    - API测试工具
    - 数据转换工具
    
    💡 输入 'help' 查看所有可用命令
    💡 输入 'exit' 退出程序
    """
    print(welcome_text)

if __name__ == "__main__":
    main()