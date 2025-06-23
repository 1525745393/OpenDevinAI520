#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能影视文件重命名工具 - 演示和测试脚本
作者: OpenHands AI
版本: 1.0.0
描述: 演示重命名工具的各种功能，包括测试用例和使用示例

功能:
1. 创建测试文件
2. 演示各种重命名场景
3. 测试正则表达式规则
4. 展示配置修改
5. 性能测试
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# 导入主程序
from video_renamer import VideoRenamer, VideoInfo


class VideoRenamerDemo:
    """
    重命名工具演示类
    
    提供各种演示和测试功能
    """
    
    def __init__(self):
        """初始化演示环境"""
        self.demo_dir = Path("demo_files")
        self.renamer = VideoRenamer()
        
        # 加载配置
        if not self.renamer.load_config():
            print("❌ 无法加载配置文件")
            sys.exit(1)
    
    def create_test_files(self) -> None:
        """
        创建测试文件
        
        生成各种格式的测试文件名，用于演示重命名功能
        """
        print("🎬 创建测试文件...")
        
        # 创建演示目录
        self.demo_dir.mkdir(exist_ok=True)
        
        # 测试文件列表 - 电影
        movie_files = [
            # 标准格式
            "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
            "Inception.2010.720p.WEBRip.x264.AAC-YTS.mp4",
            "Avengers.Endgame.2019.2160p.UHD.BluRay.x265-TERMINAL.mkv",
            
            # 括号年份格式
            "Interstellar (2014) 1080p BluRay x264.mp4",
            "The Dark Knight (2008) 720p HDTV x264.avi",
            
            # 中文电影
            "流浪地球.2019.1080p.WEBRip.x264.mkv",
            "哪吒之魔童降世.2019.720p.BluRay.x264.mp4",
            "我不是药神.2018.1080p.WEB-DL.x264.mp4",
            
            # 复杂格式
            "Spider-Man.No.Way.Home.2021.1080p.WEBRip.x264.AAC5.1-RARBG.mp4",
            "Dune.2021.IMAX.1080p.BluRay.x264.DTS-HD.MA.5.1-FGT.mkv",
        ]
        
        # 测试文件列表 - 电视剧
        tv_files = [
            # 标准S01E01格式
            "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
            "Breaking.Bad.S02E05.720p.HDTV.x264-CTU.avi",
            "The.Mandalorian.S01E01.1080p.WEBRip.x264-RARBG.mp4",
            
            # 数字格式
            "Friends.1x01.The.One.Where.Monica.Gets.a.Roommate.720p.BluRay.x264.mkv",
            "The.Office.2x03.The.Convention.1080p.WEB-DL.x264.mp4",
            
            # 中文电视剧
            "庆余年.第一季.第01集.1080p.WEB-DL.x264.mp4",
            "琅琊榜.第一季.第02集.720p.HDTV.x264.avi",
            "延禧攻略.第一季.第15集.1080p.WEBRip.x264.mkv",
            
            # 复杂格式
            "Stranger.Things.S03E08.The.Battle.of.Starcourt.1080p.NF.WEBRip.DDP5.1.x264-NTG.mkv",
            "The.Crown.S04E10.War.1080p.NF.WEB-DL.DDP5.1.x264-NTG.mp4",
        ]
        
        # 创建电影测试文件
        movie_dir = self.demo_dir / "Movies"
        movie_dir.mkdir(exist_ok=True)
        
        for filename in movie_files:
            file_path = movie_dir / filename
            file_path.touch()
            print(f"   创建: {filename}")
        
        # 创建电视剧测试文件
        tv_dir = self.demo_dir / "TV_Shows"
        tv_dir.mkdir(exist_ok=True)
        
        for filename in tv_files:
            file_path = tv_dir / filename
            file_path.touch()
            print(f"   创建: {filename}")
        
        print(f"✅ 测试文件创建完成，位置: {self.demo_dir}")
        print(f"   电影文件: {len(movie_files)} 个")
        print(f"   电视剧文件: {len(tv_files)} 个")
    
    def demo_extraction(self) -> None:
        """
        演示信息提取功能
        
        展示如何从各种文件名格式中提取影视信息
        """
        print("\n🔍 信息提取演示")
        print("=" * 60)
        
        # 测试文件名列表
        test_files = [
            "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
            "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
            "流浪地球.2019.1080p.WEBRip.x264.mkv",
            "庆余年.第一季.第01集.1080p.WEB-DL.x264.mp4",
            "Inception (2010) 720p BluRay x264.mp4",
            "Friends.1x01.The.One.Where.Monica.Gets.a.Roommate.720p.BluRay.x264.mkv"
        ]
        
        for filename in test_files:
            print(f"\n📁 原文件名: {filename}")
            
            # 提取信息
            info = self.renamer.extract_video_info(filename)
            
            # 显示提取结果
            print(f"   类型: {'电影' if info.is_movie else '电视剧'}")
            print(f"   标题: {info.title}")
            if info.year:
                print(f"   年份: {info.year}")
            if info.season:
                print(f"   季数: {info.season}")
            if info.episode:
                print(f"   集数: {info.episode}")
            if info.resolution:
                print(f"   分辨率: {info.resolution}")
            if info.quality:
                print(f"   画质: {info.quality}")
            if info.codec:
                print(f"   编码: {info.codec}")
            
            # 生成新文件名
            new_name = self.renamer.generate_new_filename(info)
            print(f"   新文件名: {new_name}")
    
    def demo_templates(self) -> None:
        """
        演示不同重命名模板的效果
        """
        print("\n🎨 重命名模板演示")
        print("=" * 60)
        
        # 测试用的视频信息
        test_cases = [
            {
                "filename": "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
                "description": "经典科幻电影"
            },
            {
                "filename": "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
                "description": "热门美剧"
            }
        ]
        
        # 获取所有模板
        movie_templates = self.renamer.config.get('naming_templates', {}).get('movie_templates', {})
        tv_templates = self.renamer.config.get('naming_templates', {}).get('tv_templates', {})
        
        for case in test_cases:
            filename = case['filename']
            description = case['description']
            
            print(f"\n📺 {description}")
            print(f"原文件名: {filename}")
            
            # 提取信息
            info = self.renamer.extract_video_info(filename)
            
            # 测试不同模板
            templates = movie_templates if info.is_movie else tv_templates
            
            for template_name, template in templates.items():
                # 临时设置模板
                if info.is_movie:
                    original_template = self.renamer.config['naming_templates']['current_movie_template']
                    self.renamer.config['naming_templates']['current_movie_template'] = template_name
                else:
                    original_template = self.renamer.config['naming_templates']['current_tv_template']
                    self.renamer.config['naming_templates']['current_tv_template'] = template_name
                
                # 生成新文件名
                new_name = self.renamer.generate_new_filename(info)
                
                print(f"   {template_name:15s}: {new_name}")
                
                # 恢复原模板
                if info.is_movie:
                    self.renamer.config['naming_templates']['current_movie_template'] = original_template
                else:
                    self.renamer.config['naming_templates']['current_tv_template'] = original_template
    
    def demo_preview_mode(self) -> None:
        """
        演示预览模式功能
        """
        print("\n👀 预览模式演示")
        print("=" * 60)
        
        # 确保测试文件存在
        if not self.demo_dir.exists():
            self.create_test_files()
        
        # 扫描电影目录
        movie_dir = self.demo_dir / "Movies"
        if movie_dir.exists():
            print(f"\n📽️ 扫描电影目录: {movie_dir}")
            movie_files = self.renamer.scan_directory(str(movie_dir))
            
            if movie_files:
                print(f"找到 {len(movie_files)} 个电影文件")
                
                # 生成预览
                preview_results = self.renamer.preview_rename(movie_files[:3])  # 只显示前3个
                
                print(f"\n预览结果 (前3个文件):")
                for i, result in enumerate(preview_results, 1):
                    print(f"\n{i}. 【{result.get('type', '未知')}】")
                    print(f"   原文件名: {result['original_name']}")
                    print(f"   新文件名: {result['new_name']}")
                    if result.get('title'):
                        print(f"   标题: {result['title']}")
                    if result.get('year'):
                        print(f"   年份: {result['year']}")
                    if result.get('resolution'):
                        print(f"   分辨率: {result['resolution']}")
        
        # 扫描电视剧目录
        tv_dir = self.demo_dir / "TV_Shows"
        if tv_dir.exists():
            print(f"\n📺 扫描电视剧目录: {tv_dir}")
            tv_files = self.renamer.scan_directory(str(tv_dir))
            
            if tv_files:
                print(f"找到 {len(tv_files)} 个电视剧文件")
                
                # 生成预览
                preview_results = self.renamer.preview_rename(tv_files[:3])  # 只显示前3个
                
                print(f"\n预览结果 (前3个文件):")
                for i, result in enumerate(preview_results, 1):
                    print(f"\n{i}. 【{result.get('type', '未知')}】")
                    print(f"   原文件名: {result['original_name']}")
                    print(f"   新文件名: {result['new_name']}")
                    if result.get('title'):
                        print(f"   标题: {result['title']}")
                    if result.get('season') and result.get('episode'):
                        print(f"   季集: S{result['season']}E{result['episode']}")
                    if result.get('resolution'):
                        print(f"   分辨率: {result['resolution']}")
    
    def demo_dry_run(self) -> None:
        """
        演示干运行模式
        """
        print("\n🧪 Dry-run 模式演示")
        print("=" * 60)
        
        # 确保测试文件存在
        if not self.demo_dir.exists():
            self.create_test_files()
        
        # 获取所有测试文件
        all_files = []
        for file_path in self.demo_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.mkv', '.avi']:
                all_files.append(str(file_path))
        
        if not all_files:
            print("❌ 没有找到测试文件")
            return
        
        print(f"找到 {len(all_files)} 个测试文件")
        
        # 执行干运行
        print(f"\n🔄 执行 Dry-run 模式...")
        results = self.renamer.rename_files(all_files[:5], dry_run=True)  # 只处理前5个
        
        # 显示结果
        print(f"\n📊 Dry-run 结果:")
        print(f"   总文件数: {results['total']}")
        print(f"   成功: {results['success']}")
        print(f"   失败: {results['failed']}")
        print(f"   跳过: {results['skipped']}")
        
        if results['errors']:
            print(f"\n❌ 错误信息:")
            for error in results['errors']:
                print(f"   • {error}")
        
        print(f"\n💡 这是预览模式，没有实际修改文件")
    
    def demo_regex_testing(self) -> None:
        """
        演示正则表达式测试功能
        """
        print("\n🔧 正则表达式测试演示")
        print("=" * 60)
        
        # 测试文件名
        test_filenames = [
            "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
            "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
            "Inception (2010) 720p BluRay x264.mp4",
            "Friends.1x01.The.One.Where.Monica.Gets.a.Roommate.720p.BluRay.x264.mkv",
            "流浪地球.2019.1080p.WEBRip.x264.mkv",
            "庆余年.第一季.第01集.1080p.WEB-DL.x264.mp4"
        ]
        
        # 获取正则表达式规则
        movie_patterns = self.renamer.config.get('extraction_rules', {}).get('movie_patterns', [])
        tv_patterns = self.renamer.config.get('extraction_rules', {}).get('tv_patterns', [])
        
        print("📽️ 电影模式正则表达式测试:")
        for pattern_config in movie_patterns:
            pattern_name = pattern_config.get('name', '未命名')
            pattern = pattern_config.get('pattern', '')
            
            print(f"\n   规则: {pattern_name}")
            print(f"   正则: {pattern}")
            
            for filename in test_filenames:
                import re
                try:
                    match = re.search(pattern, Path(filename).stem, re.IGNORECASE)
                    if match:
                        print(f"   ✅ 匹配: {filename}")
                        groups = pattern_config.get('groups', {})
                        for key, group_num in groups.items():
                            if group_num <= len(match.groups()):
                                value = match.group(group_num).strip()
                                print(f"      {key}: {value}")
                        break
                except re.error as e:
                    print(f"   ❌ 正则错误: {e}")
        
        print(f"\n📺 电视剧模式正则表达式测试:")
        for pattern_config in tv_patterns:
            pattern_name = pattern_config.get('name', '未命名')
            pattern = pattern_config.get('pattern', '')
            
            print(f"\n   规则: {pattern_name}")
            print(f"   正则: {pattern}")
            
            for filename in test_filenames:
                import re
                try:
                    match = re.search(pattern, Path(filename).stem, re.IGNORECASE)
                    if match:
                        print(f"   ✅ 匹配: {filename}")
                        groups = pattern_config.get('groups', {})
                        for key, group_num in groups.items():
                            if group_num <= len(match.groups()):
                                value = match.group(group_num).strip()
                                print(f"      {key}: {value}")
                        break
                except re.error as e:
                    print(f"   ❌ 正则错误: {e}")
    
    def demo_config_modification(self) -> None:
        """
        演示配置修改功能
        """
        print("\n⚙️ 配置修改演示")
        print("=" * 60)
        
        # 显示当前配置
        current_movie_template = self.renamer.config.get('naming_templates', {}).get('current_movie_template', '未设置')
        current_tv_template = self.renamer.config.get('naming_templates', {}).get('current_tv_template', '未设置')
        backup_enabled = self.renamer.config.get('app_settings', {}).get('backup_enabled', False)
        
        print(f"当前配置:")
        print(f"   电影模板: {current_movie_template}")
        print(f"   电视剧模板: {current_tv_template}")
        print(f"   备份功能: {'启用' if backup_enabled else '禁用'}")
        
        # 演示模板切换
        print(f"\n🎨 可用的电影模板:")
        movie_templates = self.renamer.config.get('naming_templates', {}).get('movie_templates', {})
        for i, (name, template) in enumerate(movie_templates.items(), 1):
            current_mark = " (当前)" if name == current_movie_template else ""
            print(f"   {i}. {name}{current_mark}")
            print(f"      格式: {template}")
        
        print(f"\n📺 可用的电视剧模板:")
        tv_templates = self.renamer.config.get('naming_templates', {}).get('tv_templates', {})
        for i, (name, template) in enumerate(tv_templates.items(), 1):
            current_mark = " (当前)" if name == current_tv_template else ""
            print(f"   {i}. {name}{current_mark}")
            print(f"      格式: {template}")
        
        # 演示模板效果对比
        print(f"\n🔄 模板效果对比:")
        test_filename = "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv"
        info = self.renamer.extract_video_info(test_filename)
        
        print(f"测试文件: {test_filename}")
        
        for template_name, template in movie_templates.items():
            # 临时设置模板
            original_template = self.renamer.config['naming_templates']['current_movie_template']
            self.renamer.config['naming_templates']['current_movie_template'] = template_name
            
            # 生成新文件名
            new_name = self.renamer.generate_new_filename(info)
            
            print(f"   {template_name:15s}: {new_name}")
            
            # 恢复原模板
            self.renamer.config['naming_templates']['current_movie_template'] = original_template
    
    def demo_performance_test(self) -> None:
        """
        演示性能测试
        """
        print("\n⚡ 性能测试演示")
        print("=" * 60)
        
        import time
        
        # 创建大量测试文件名
        test_filenames = []
        
        # 生成电影文件名
        for i in range(100):
            test_filenames.append(f"Movie.{2000+i%23}.1080p.BluRay.x264-GROUP{i}.mkv")
        
        # 生成电视剧文件名
        for i in range(100):
            season = (i % 5) + 1
            episode = (i % 20) + 1
            test_filenames.append(f"TV.Show.S{season:02d}E{episode:02d}.1080p.WEBRip.x264-GROUP{i}.mp4")
        
        print(f"生成 {len(test_filenames)} 个测试文件名")
        
        # 测试信息提取性能
        print(f"\n🔍 测试信息提取性能...")
        start_time = time.time()
        
        extracted_info = []
        for filename in test_filenames:
            info = self.renamer.extract_video_info(filename)
            extracted_info.append(info)
        
        extraction_time = time.time() - start_time
        
        print(f"   提取 {len(test_filenames)} 个文件信息耗时: {extraction_time:.2f} 秒")
        print(f"   平均每个文件: {(extraction_time/len(test_filenames)*1000):.2f} 毫秒")
        
        # 测试文件名生成性能
        print(f"\n🎨 测试文件名生成性能...")
        start_time = time.time()
        
        new_filenames = []
        for info in extracted_info:
            new_name = self.renamer.generate_new_filename(info)
            new_filenames.append(new_name)
        
        generation_time = time.time() - start_time
        
        print(f"   生成 {len(extracted_info)} 个新文件名耗时: {generation_time:.2f} 秒")
        print(f"   平均每个文件: {(generation_time/len(extracted_info)*1000):.2f} 毫秒")
        
        # 显示统计信息
        movie_count = sum(1 for info in extracted_info if info.is_movie)
        tv_count = len(extracted_info) - movie_count
        
        print(f"\n📊 处理统计:")
        print(f"   电影文件: {movie_count} 个")
        print(f"   电视剧文件: {tv_count} 个")
        print(f"   总处理时间: {(extraction_time + generation_time):.2f} 秒")
    
    def cleanup_demo_files(self) -> None:
        """
        清理演示文件
        """
        if self.demo_dir.exists():
            print(f"\n🧹 清理演示文件...")
            shutil.rmtree(self.demo_dir)
            print(f"✅ 演示文件已清理: {self.demo_dir}")
        else:
            print(f"📁 演示目录不存在，无需清理")
    
    def run_all_demos(self) -> None:
        """
        运行所有演示
        """
        print("🎬 智能影视文件重命名工具 - 完整演示")
        print("=" * 70)
        
        try:
            # 1. 创建测试文件
            self.create_test_files()
            
            # 2. 信息提取演示
            self.demo_extraction()
            
            # 3. 模板演示
            self.demo_templates()
            
            # 4. 预览模式演示
            self.demo_preview_mode()
            
            # 5. Dry-run 演示
            self.demo_dry_run()
            
            # 6. 正则表达式测试
            self.demo_regex_testing()
            
            # 7. 配置修改演示
            self.demo_config_modification()
            
            # 8. 性能测试
            self.demo_performance_test()
            
            print(f"\n🎉 所有演示完成！")
            
        except Exception as e:
            print(f"\n❌ 演示过程中发生错误: {e}")
            
        finally:
            # 询问是否清理文件
            try:
                cleanup = input(f"\n🗑️  是否清理演示文件？(y/N): ").strip().lower()
                if cleanup == 'y':
                    self.cleanup_demo_files()
            except KeyboardInterrupt:
                print(f"\n\n👋 演示结束")
    
    def interactive_demo(self) -> None:
        """
        交互式演示菜单
        """
        print("🎬 智能影视文件重命名工具 - 演示菜单")
        
        while True:
            print(f"\n{'='*50}")
            print("请选择演示功能:")
            print("1. 创建测试文件")
            print("2. 信息提取演示")
            print("3. 重命名模板演示")
            print("4. 预览模式演示")
            print("5. Dry-run 模式演示")
            print("6. 正则表达式测试")
            print("7. 配置修改演示")
            print("8. 性能测试")
            print("9. 运行所有演示")
            print("10. 清理演示文件")
            print("11. 退出")
            print(f"{'='*50}")
            
            try:
                choice = input("请输入选择 (1-11): ").strip()
                
                if choice == '1':
                    self.create_test_files()
                elif choice == '2':
                    self.demo_extraction()
                elif choice == '3':
                    self.demo_templates()
                elif choice == '4':
                    self.demo_preview_mode()
                elif choice == '5':
                    self.demo_dry_run()
                elif choice == '6':
                    self.demo_regex_testing()
                elif choice == '7':
                    self.demo_config_modification()
                elif choice == '8':
                    self.demo_performance_test()
                elif choice == '9':
                    self.run_all_demos()
                elif choice == '10':
                    self.cleanup_demo_files()
                elif choice == '11':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请输入 1-11")
                    
            except KeyboardInterrupt:
                print(f"\n\n👋 演示已退出")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")


def main():
    """
    主函数
    """
    print("🎬 智能影视文件重命名工具 - 演示程序")
    print("   作者: OpenHands AI")
    print("   功能: 演示重命名工具的各种功能")
    
    # 创建演示实例
    demo = VideoRenamerDemo()
    
    # 运行交互式演示
    demo.interactive_demo()


if __name__ == "__main__":
    main()