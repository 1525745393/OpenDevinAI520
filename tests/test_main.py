"""
主程序测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import print_welcome


def test_print_welcome(capsys):
    """测试欢迎信息打印"""
    print_welcome()
    captured = capsys.readouterr()
    
    assert "OpenDevinAI520" in captured.out
    assert "实用工具开发平台" in captured.out
    assert "人人为我，我为人人" in captured.out


def test_project_structure():
    """测试项目结构"""
    project_root = Path(__file__).parent.parent
    
    # 检查主要目录
    assert (project_root / "src").exists()
    assert (project_root / "src" / "tools").exists()
    assert (project_root / "src" / "utils").exists()
    assert (project_root / "docs").exists()
    assert (project_root / "tests").exists()
    
    # 检查主要文件
    assert (project_root / "README.md").exists()
    assert (project_root / "LICENSE").exists()
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "src" / "main.py").exists()


def test_imports():
    """测试主要模块导入"""
    try:
        from src.utils.logger import setup_logger
        from src.utils.config import load_config
        from src.tools import ToolManager
        
        # 测试基本功能
        logger = setup_logger("test")
        assert logger is not None
        
        config = load_config()
        assert isinstance(config, dict)
        assert "app" in config
        
        tool_manager = ToolManager(config)
        assert tool_manager is not None
        
    except ImportError as e:
        pytest.fail(f"导入失败: {e}")