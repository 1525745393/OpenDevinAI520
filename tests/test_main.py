"""
OpenDevinAI520 主程序测试
"""

import unittest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestMain(unittest.TestCase):
    """主程序测试类"""
    
    def test_import_main(self):
        """测试主程序模块导入"""
        try:
            import main
            self.assertTrue(True)
        except ImportError:
            self.fail("无法导入主程序模块")
    
    def test_banner_function(self):
        """测试横幅显示函数"""
        import main
        try:
            main.show_banner()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"横幅显示函数执行失败: {e}")

if __name__ == '__main__':
    unittest.main()