#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群晖Python应用 - 使用示例
作者: OpenHands AI
描述: 演示如何使用和扩展主应用程序

这个文件展示了如何：
1. 导入主应用类
2. 自定义配置
3. 添加自己的业务逻辑
4. 处理配置更新
"""

from synology_app import SynologyApp
import time
import json


class MyCustomApp(SynologyApp):
    """
    自定义应用类
    
    继承自SynologyApp，可以添加自己的功能
    """
    
    def __init__(self):
        """初始化自定义应用"""
        super().__init__()
        self.logger.info("自定义应用初始化完成")
    
    def add_custom_config(self):
        """
        添加自定义配置项
        
        演示如何添加新的配置选项
        """
        # 添加自定义配置节
        custom_settings = {
            "my_feature_enabled": True,
            "data_source": "local_files",
            "processing_mode": "batch",
            "output_format": "json",
            "max_file_size": 100  # MB
        }
        
        # 更新配置
        for key, value in custom_settings.items():
            self.update_config_value('custom', key, value)
        
        self.logger.info("自定义配置添加完成")
    
    def my_custom_task(self):
        """
        自定义任务示例
        
        这里可以添加你的具体业务逻辑
        """
        # 读取配置
        feature_enabled = self.get_config_value('custom', 'my_feature_enabled', False)
        data_source = self.get_config_value('custom', 'data_source', 'local_files')
        
        if not feature_enabled:
            self.logger.info("自定义功能未启用")
            return
        
        self.logger.info(f"开始执行自定义任务，数据源: {data_source}")
        
        # 模拟一些处理工作
        print(f"   🔄 正在处理数据源: {data_source}")
        time.sleep(2)  # 模拟处理时间
        
        # 模拟处理结果
        result = {
            "processed_files": 5,
            "total_size": "25.6 MB",
            "processing_time": "2.1 seconds",
            "status": "success"
        }
        
        print(f"   ✅ 处理完成: {result}")
        self.logger.info(f"自定义任务完成: {result}")
        
        return result
    
    def run_main_application(self):
        """
        重写主应用逻辑
        
        添加自定义的业务流程
        """
        self.logger.info("开始运行自定义主应用程序")
        
        # 添加自定义配置
        self.add_custom_config()
        
        # 获取基本设置
        debug_mode = self.get_config_value('app_settings', 'debug_mode', False)
        check_interval = self.get_config_value('app_settings', 'check_interval', 60)
        
        print(f"\n🚀 自定义应用启动成功！")
        print(f"   调试模式: {'开启' if debug_mode else '关闭'}")
        print(f"   检查间隔: {check_interval}秒")
        print(f"   自定义功能: 已启用")
        
        try:
            print(f"\n💡 应用正在运行中...")
            print(f"   按 Ctrl+C 可以停止程序")
            
            counter = 0
            while True:
                counter += 1
                
                print(f"\n--- 第 {counter} 次循环 ---")
                
                # 执行自定义任务
                self.my_custom_task()
                
                # 显示系统状态
                if debug_mode:
                    self.show_system_status()
                
                # 等待下次执行
                print(f"   ⏰ 等待 {check_interval} 秒后继续...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print(f"\n\n👋 自定义应用已停止")
            self.logger.info("用户手动停止自定义应用")
            
        except Exception as e:
            self.logger.error(f"自定义应用运行时发生错误: {e}")
            print(f"\n❌ 应用发生错误: {e}")
    
    def show_system_status(self):
        """
        显示系统状态信息
        
        在调试模式下显示详细的系统信息
        """
        import os
        import psutil
        
        try:
            # 获取系统信息
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"\n📊 系统状态:")
            print(f"   CPU使用率: {cpu_percent}%")
            print(f"   内存使用率: {memory.percent}%")
            print(f"   磁盘使用率: {disk.percent}%")
            
        except ImportError:
            # 如果没有安装psutil，显示基本信息
            print(f"\n📊 系统状态:")
            print(f"   进程ID: {os.getpid()}")
            print(f"   工作目录: {os.getcwd()}")
        
        except Exception as e:
            self.logger.warning(f"获取系统状态失败: {e}")


def demo_config_operations():
    """
    演示配置操作
    
    展示如何读取、修改和保存配置
    """
    print("\n" + "=" * 50)
    print("📋 配置操作演示")
    print("=" * 50)
    
    # 创建应用实例
    app = SynologyApp()
    
    # 加载配置
    if app.load_config():
        print("✅ 配置加载成功")
    else:
        print("❌ 配置加载失败")
        return
    
    # 读取配置示例
    print(f"\n📖 读取配置示例:")
    app_name = app.get_config_value('app_info', 'name', '未知应用')
    debug_mode = app.get_config_value('app_settings', 'debug_mode', False)
    port = app.get_config_value('network', 'port', 8080)
    
    print(f"   应用名称: {app_name}")
    print(f"   调试模式: {debug_mode}")
    print(f"   监听端口: {port}")
    
    # 修改配置示例
    print(f"\n✏️ 修改配置示例:")
    
    # 启用调试模式
    if app.update_config_value('app_settings', 'debug_mode', True):
        print("   ✅ 调试模式已启用")
    
    # 修改检查间隔
    if app.update_config_value('app_settings', 'check_interval', 30):
        print("   ✅ 检查间隔已修改为30秒")
    
    # 添加自定义配置
    if app.update_config_value('custom', 'demo_setting', 'Hello World'):
        print("   ✅ 添加了自定义配置项")
    
    # 显示修改后的配置
    print(f"\n📋 修改后的配置:")
    debug_mode = app.get_config_value('app_settings', 'debug_mode', False)
    interval = app.get_config_value('app_settings', 'check_interval', 60)
    demo_setting = app.get_config_value('custom', 'demo_setting', '')
    
    print(f"   调试模式: {debug_mode}")
    print(f"   检查间隔: {interval}秒")
    print(f"   演示设置: {demo_setting}")


def main():
    """
    主函数 - 演示不同的使用方式
    """
    print("🎯 群晖Python应用 - 使用示例")
    print("   这个脚本演示了如何使用和扩展主应用程序")
    
    while True:
        print(f"\n" + "=" * 40)
        print("请选择要演示的功能:")
        print("1. 运行原始应用")
        print("2. 运行自定义应用")
        print("3. 配置操作演示")
        print("4. 退出")
        print("=" * 40)
        
        try:
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == '1':
                print(f"\n🚀 启动原始应用...")
                app = SynologyApp()
                app.run()
                
            elif choice == '2':
                print(f"\n🚀 启动自定义应用...")
                custom_app = MyCustomApp()
                custom_app.run()
                
            elif choice == '3':
                demo_config_operations()
                
            elif choice == '4':
                print(f"\n👋 再见！")
                break
                
            else:
                print(f"\n❌ 无效选择，请输入 1-4")
                
        except KeyboardInterrupt:
            print(f"\n\n👋 程序已退出")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()