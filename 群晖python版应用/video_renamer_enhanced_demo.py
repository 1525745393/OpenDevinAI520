#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能影视文件重命名工具 - 增强版演示脚本
作者: OpenHands AI
版本: 2.0.0
描述: 演示增强版重命名工具的API集成功能

功能:
1. API连接测试
2. 元数据获取演示
3. NFO文件生成演示
4. 海报下载演示
5. 增强模板演示
6. 性能测试
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# 导入增强版主程序
try:
    from video_renamer_enhanced import EnhancedVideoRenamer, MovieMetadata, TVMetadata
except ImportError:
    print("❌ 无法导入增强版重命名工具，请确保 video_renamer_enhanced.py 文件存在")
    sys.exit(1)


class EnhancedVideoRenamerDemo:
    """
    增强版重命名工具演示类
    
    提供各种演示和测试功能
    """
    
    def __init__(self):
        """初始化演示环境"""
        self.demo_dir = Path("enhanced_demo_files")
        self.renamer = EnhancedVideoRenamer()
        
        # 加载配置
        if not self.renamer.load_config():
            print("❌ 无法加载配置文件")
            sys.exit(1)
    
    def create_test_files(self) -> None:
        """
        创建测试文件
        
        生成各种格式的测试文件名，用于演示API功能
        """
        print("🎬 创建增强版测试文件...")
        
        # 创建演示目录
        self.demo_dir.mkdir(exist_ok=True)
        
        # 知名电影测试文件（便于API匹配）
        movie_files = [
            # 好莱坞经典
            "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
            "Inception.2010.720p.WEBRip.x264.AAC-YTS.mp4",
            "The.Shawshank.Redemption.1994.1080p.BluRay.x264.mkv",
            "Pulp.Fiction.1994.720p.BluRay.x264-GROUP.avi",
            "The.Dark.Knight.2008.1080p.BluRay.x264.mp4",
            
            # 中文电影
            "流浪地球.2019.1080p.WEBRip.x264.mkv",
            "哪吒之魔童降世.2019.720p.BluRay.x264.mp4",
            "我不是药神.2018.1080p.WEB-DL.x264.mp4",
            "让子弹飞.2010.1080p.BluRay.x264.mkv",
            "无间道.2002.720p.BluRay.x264.avi",
            
            # 动画电影
            "Spirited.Away.2001.1080p.BluRay.x264.mkv",
            "Your.Name.2016.1080p.BluRay.x264.mp4",
            "Frozen.2013.720p.BluRay.x264.mkv",
        ]
        
        # 知名电视剧测试文件
        tv_files = [
            # 美剧
            "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
            "Breaking.Bad.S01E01.720p.BluRay.x264-DEMAND.avi",
            "Friends.S01E01.The.One.Where.Monica.Gets.a.Roommate.720p.BluRay.x264.mkv",
            "The.Office.US.S01E01.720p.WEB-DL.x264.mp4",
            "Stranger.Things.S01E01.1080p.NF.WEBRip.x264.mkv",
            
            # 中文电视剧
            "琅琊榜.第一季.第01集.1080p.WEB-DL.x264.mp4",
            "庆余年.第一季.第01集.720p.HDTV.x264.avi",
            "延禧攻略.第一季.第01集.1080p.WEBRip.x264.mkv",
            "甄嬛传.第一季.第01集.720p.HDTV.x264.mp4",
            
            # 日韩剧
            "半泽直树.第一季.第01集.1080p.WEB-DL.x264.mkv",
            "请回答1988.第一季.第01集.720p.HDTV.x264.mp4",
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
        
        print(f"✅ 增强版测试文件创建完成，位置: {self.demo_dir}")
        print(f"   电影文件: {len(movie_files)} 个")
        print(f"   电视剧文件: {len(tv_files)} 个")
        print(f"   这些文件名都是知名影视作品，便于API匹配测试")
    
    def demo_api_connections(self) -> None:
        """
        演示API连接功能
        """
        print("\n🌐 API连接演示")
        print("=" * 60)
        
        # 检查API配置状态
        api_settings = self.renamer.config.get("api_settings", {})
        
        print("📋 当前API配置状态:")
        
        # TMDb状态
        tmdb_config = api_settings.get("tmdb", {})
        tmdb_enabled = tmdb_config.get("enabled", False)
        tmdb_key = tmdb_config.get("api_key", "")
        
        print(f"   TMDb API: {'✅ 启用' if tmdb_enabled else '❌ 禁用'}")
        if tmdb_enabled:
            print(f"   TMDb 密钥: {'✅ 已配置' if tmdb_key else '❌ 未配置'}")
        
        # 豆瓣状态
        douban_config = api_settings.get("douban", {})
        douban_enabled = douban_config.get("enabled", False)
        print(f"   豆瓣 API: {'✅ 启用' if douban_enabled else '❌ 禁用'}")
        
        # 测试API连接
        if tmdb_enabled and tmdb_key:
            print(f"\n🔍 测试TMDb连接...")
            self._test_tmdb_api()
        else:
            print(f"\n⚠️  TMDb API未配置，跳过测试")
            print(f"   配置方法: 程序菜单 -> 4 -> 1")
        
        if douban_enabled:
            print(f"\n🔍 测试豆瓣连接...")
            self._test_douban_api()
        else:
            print(f"\n⚠️  豆瓣API未启用，跳过测试")
            print(f"   启用方法: 程序菜单 -> 4 -> 2")
    
    def _test_tmdb_api(self) -> None:
        """测试TMDb API"""
        try:
            # 初始化组件
            self.renamer._initialize_components()
            
            if not self.renamer.metadata_fetcher.tmdb_client:
                print("❌ TMDb客户端初始化失败")
                return
            
            # 测试搜索电影
            print("   搜索电影: The Matrix")
            results = self.renamer.metadata_fetcher.tmdb_client.search_movie("The Matrix", 1999)
            
            if results:
                print(f"   ✅ 搜索成功，找到 {len(results)} 个结果")
                best_match = results[0]
                print(f"   最佳匹配: {best_match.get('title')} ({best_match.get('release_date', '')[:4]})")
                print(f"   评分: {best_match.get('vote_average', 0):.1f}")
                
                # 测试获取详细信息
                movie_id = best_match["id"]
                details = self.renamer.metadata_fetcher.tmdb_client.get_movie_details(movie_id)
                if details:
                    print(f"   ✅ 详细信息获取成功")
                    print(f"   时长: {details.get('runtime', 0)} 分钟")
                    print(f"   类型: {', '.join([g['name'] for g in details.get('genres', [])])}")
                else:
                    print(f"   ❌ 详细信息获取失败")
            else:
                print("   ❌ 搜索失败或无结果")
                
        except Exception as e:
            print(f"   ❌ TMDb API测试失败: {e}")
    
    def _test_douban_api(self) -> None:
        """测试豆瓣API"""
        try:
            # 初始化组件
            self.renamer._initialize_components()
            
            if not self.renamer.metadata_fetcher.douban_client:
                print("❌ 豆瓣客户端初始化失败")
                return
            
            # 测试搜索电影
            print("   搜索电影: 肖申克的救赎")
            results = self.renamer.metadata_fetcher.douban_client.search_movie("肖申克的救赎")
            
            if results:
                print(f"   ✅ 搜索成功，找到 {len(results)} 个结果")
                best_match = results[0]
                print(f"   最佳匹配: {best_match.get('title')}")
                rating = best_match.get('rating', {})
                if rating:
                    print(f"   评分: {rating.get('average', 0):.1f}")
                
                # 测试获取详细信息
                movie_id = best_match["id"]
                details = self.renamer.metadata_fetcher.douban_client.get_movie_details(movie_id)
                if details:
                    print(f"   ✅ 详细信息获取成功")
                    print(f"   年份: {details.get('year', '未知')}")
                    genres = details.get('genres', [])
                    if genres:
                        print(f"   类型: {', '.join(genres)}")
                else:
                    print(f"   ❌ 详细信息获取失败")
            else:
                print("   ❌ 搜索失败或无结果")
                
        except Exception as e:
            print(f"   ❌ 豆瓣API测试失败: {e}")
    
    def demo_metadata_extraction(self) -> None:
        """
        演示元数据提取功能
        """
        print("\n🔍 元数据提取演示")
        print("=" * 60)
        
        # 测试文件名列表
        test_files = [
            "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
            "流浪地球.2019.1080p.WEBRip.x264.mkv",
            "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
            "琅琊榜.第一季.第01集.1080p.WEB-DL.x264.mp4"
        ]
        
        for filename in test_files:
            print(f"\n📁 处理文件: {filename}")
            
            try:
                # 提取增强信息
                basic_info, api_metadata = self.renamer.extract_video_info_enhanced(filename)
                
                # 显示基础信息
                print(f"   类型: {'电影' if basic_info.is_movie else '电视剧'}")
                print(f"   提取标题: {basic_info.title}")
                if basic_info.year:
                    print(f"   提取年份: {basic_info.year}")
                if basic_info.season and basic_info.episode:
                    print(f"   季集信息: S{basic_info.season}E{basic_info.episode}")
                
                # 显示API元数据
                if api_metadata:
                    print(f"   🌐 API数据: ✅ 已获取")
                    print(f"   标准标题: {api_metadata.title}")
                    if hasattr(api_metadata, 'chinese_title') and api_metadata.chinese_title:
                        print(f"   中文标题: {api_metadata.chinese_title}")
                    if hasattr(api_metadata, 'original_title') and api_metadata.original_title:
                        print(f"   原始标题: {api_metadata.original_title}")
                    
                    if api_metadata.year:
                        print(f"   准确年份: {api_metadata.year}")
                    
                    # 评分信息
                    ratings = []
                    if api_metadata.rating_tmdb > 0:
                        ratings.append(f"TMDb: {api_metadata.rating_tmdb:.1f}")
                    if api_metadata.rating_douban > 0:
                        ratings.append(f"豆瓣: {api_metadata.rating_douban:.1f}")
                    if ratings:
                        print(f"   评分: {' | '.join(ratings)}")
                    
                    # 其他信息
                    if api_metadata.genres:
                        print(f"   类型: {', '.join(api_metadata.genres[:3])}")
                    
                    director = getattr(api_metadata, 'director', '') or getattr(api_metadata, 'creator', '')
                    if director:
                        print(f"   导演: {director}")
                    
                    # ID信息
                    ids = []
                    if api_metadata.tmdb_id:
                        ids.append(f"TMDb: {api_metadata.tmdb_id}")
                    if hasattr(api_metadata, 'douban_id') and api_metadata.douban_id:
                        ids.append(f"豆瓣: {api_metadata.douban_id}")
                    if ids:
                        print(f"   数据库ID: {' | '.join(ids)}")
                    
                    # 生成增强文件名
                    new_filename = self.renamer.generate_new_filename_enhanced(basic_info, api_metadata)
                    print(f"   增强文件名: {new_filename}")
                else:
                    print(f"   🌐 API数据: ❌ 未获取")
                    # 生成基础文件名
                    new_filename = self.renamer.generate_new_filename(basic_info)
                    print(f"   基础文件名: {new_filename}")
                
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
            
            # 添加延迟避免API限制
            time.sleep(1)
    
    def demo_enhanced_templates(self) -> None:
        """
        演示增强版模板功能
        """
        print("\n🎨 增强版模板演示")
        print("=" * 60)
        
        # 测试用例
        test_cases = [
            {
                "filename": "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
                "description": "经典科幻电影 - The Matrix"
            },
            {
                "filename": "流浪地球.2019.1080p.WEBRip.x264.mkv",
                "description": "中国科幻电影 - 流浪地球"
            }
        ]
        
        # 获取增强版模板
        movie_templates = self.renamer.config.get('naming_templates', {}).get('movie_templates', {})
        
        for case in test_cases:
            filename = case['filename']
            description = case['description']
            
            print(f"\n📺 {description}")
            print(f"原文件名: {filename}")
            
            try:
                # 提取增强信息
                basic_info, api_metadata = self.renamer.extract_video_info_enhanced(filename)
                
                if api_metadata:
                    print(f"API数据: ✅ 已获取")
                    
                    # 测试不同的增强模板
                    enhanced_templates = {
                        "enhanced_synology": "{chinese_title} {title} ({year}) [{resolution}] [{quality}] [评分{rating}].{ext}",
                        "metadata_rich": "{title} ({year}) [TMDb{tmdb_rating}] [豆瓣{douban_rating}] [{resolution}].{ext}",
                        "chinese_preferred": "{chinese_title} ({year}) [{resolution}] [{quality}].{ext}"
                    }
                    
                    for template_name, template in enhanced_templates.items():
                        # 临时设置模板
                        original_template = self.renamer.config['naming_templates']['current_movie_template']
                        self.renamer.config['naming_templates']['movie_templates'][template_name] = template
                        self.renamer.config['naming_templates']['current_movie_template'] = template_name
                        
                        # 生成新文件名
                        new_name = self.renamer.generate_new_filename_enhanced(basic_info, api_metadata)
                        
                        print(f"   {template_name:20s}: {new_name}")
                        
                        # 恢复原模板
                        self.renamer.config['naming_templates']['current_movie_template'] = original_template
                else:
                    print(f"API数据: ❌ 未获取，使用基础模板")
                    new_name = self.renamer.generate_new_filename(basic_info)
                    print(f"   基础模板: {new_name}")
                
            except Exception as e:
                print(f"   ❌ 模板演示失败: {e}")
            
            # 添加延迟
            time.sleep(1)
    
    def demo_nfo_generation(self) -> None:
        """
        演示NFO文件生成功能
        """
        print("\n📄 NFO文件生成演示")
        print("=" * 60)
        
        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # 测试电影NFO生成
            print("🎬 电影NFO生成测试:")
            movie_filename = "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv"
            movie_path = temp_dir / movie_filename
            movie_path.touch()
            
            # 获取元数据
            basic_info, api_metadata = self.renamer.extract_video_info_enhanced(movie_filename)
            
            if api_metadata and isinstance(api_metadata, MovieMetadata):
                # 生成NFO文件
                success = self.renamer.nfo_generator.generate_movie_nfo(api_metadata, movie_path)
                
                if success:
                    nfo_path = movie_path.with_suffix('.nfo')
                    print(f"   ✅ NFO文件生成成功: {nfo_path.name}")
                    
                    # 显示NFO内容
                    if nfo_path.exists():
                        with open(nfo_path, 'r', encoding='utf-8') as f:
                            nfo_content = f.read()
                        
                        print(f"   📄 NFO文件内容预览:")
                        lines = nfo_content.split('\n')
                        for line in lines[:15]:  # 只显示前15行
                            if line.strip():
                                print(f"      {line}")
                        if len(lines) > 15:
                            print(f"      ... (共{len(lines)}行)")
                else:
                    print(f"   ❌ NFO文件生成失败")
            else:
                print(f"   ⚠️  无API数据，跳过NFO生成")
            
            # 测试电视剧NFO生成
            print(f"\n📺 电视剧NFO生成测试:")
            tv_filename = "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv"
            tv_path = temp_dir / tv_filename
            tv_path.touch()
            
            # 获取元数据
            basic_info, api_metadata = self.renamer.extract_video_info_enhanced(tv_filename)
            
            if api_metadata and isinstance(api_metadata, TVMetadata):
                # 生成NFO文件
                success = self.renamer.nfo_generator.generate_tv_nfo(api_metadata, tv_path)
                
                if success:
                    nfo_path = tv_path.with_suffix('.nfo')
                    print(f"   ✅ NFO文件生成成功: {nfo_path.name}")
                    
                    # 显示NFO内容
                    if nfo_path.exists():
                        with open(nfo_path, 'r', encoding='utf-8') as f:
                            nfo_content = f.read()
                        
                        print(f"   📄 NFO文件内容预览:")
                        lines = nfo_content.split('\n')
                        for line in lines[:10]:  # 只显示前10行
                            if line.strip():
                                print(f"      {line}")
                        if len(lines) > 10:
                            print(f"      ... (共{len(lines)}行)")
                else:
                    print(f"   ❌ NFO文件生成失败")
            else:
                print(f"   ⚠️  无API数据，跳过NFO生成")
            
        except Exception as e:
            print(f"❌ NFO生成演示失败: {e}")
        
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def demo_poster_download(self) -> None:
        """
        演示海报下载功能
        """
        print("\n🖼️ 海报下载演示")
        print("=" * 60)
        
        # 创建临时目录
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            # 测试海报下载
            print("🎬 电影海报下载测试:")
            movie_filename = "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv"
            movie_path = temp_dir / movie_filename
            movie_path.touch()
            
            # 获取元数据
            basic_info, api_metadata = self.renamer.extract_video_info_enhanced(movie_filename)
            
            if api_metadata and api_metadata.poster_url:
                print(f"   海报URL: {api_metadata.poster_url}")
                
                # 下载海报
                success = self.renamer.poster_downloader.download_poster(
                    api_metadata.poster_url, movie_path, "poster"
                )
                
                if success:
                    poster_path = movie_path.with_name(f"{movie_path.stem}-poster.jpg")
                    print(f"   ✅ 海报下载成功: {poster_path.name}")
                    
                    # 检查文件大小
                    if poster_path.exists():
                        file_size = poster_path.stat().st_size
                        print(f"   文件大小: {file_size / 1024:.1f} KB")
                else:
                    print(f"   ❌ 海报下载失败")
                
                # 下载背景图
                if api_metadata.backdrop_url:
                    print(f"   背景图URL: {api_metadata.backdrop_url}")
                    
                    success = self.renamer.poster_downloader.download_poster(
                        api_metadata.backdrop_url, movie_path, "fanart"
                    )
                    
                    if success:
                        fanart_path = movie_path.with_name(f"{movie_path.stem}-fanart.jpg")
                        print(f"   ✅ 背景图下载成功: {fanart_path.name}")
                        
                        # 检查文件大小
                        if fanart_path.exists():
                            file_size = fanart_path.stat().st_size
                            print(f"   文件大小: {file_size / 1024:.1f} KB")
                    else:
                        print(f"   ❌ 背景图下载失败")
            else:
                print(f"   ⚠️  无海报URL，跳过下载")
            
        except Exception as e:
            print(f"❌ 海报下载演示失败: {e}")
        
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def demo_enhanced_preview(self) -> None:
        """
        演示增强版预览功能
        """
        print("\n👀 增强版预览演示")
        print("=" * 60)
        
        # 确保测试文件存在
        if not self.demo_dir.exists():
            self.create_test_files()
        
        # 扫描电影目录
        movie_dir = self.demo_dir / "Movies"
        if movie_dir.exists():
            print(f"📽️ 扫描电影目录: {movie_dir}")
            movie_files = self.renamer.scan_directory(str(movie_dir))
            
            if movie_files:
                print(f"找到 {len(movie_files)} 个电影文件")
                
                # 生成增强预览（只处理前3个文件）
                print(f"\n🌐 正在获取API元数据，请稍候...")
                preview_results = self.renamer.preview_rename_enhanced(movie_files[:3])
                
                print(f"\n增强版预览结果:")
                for i, result in enumerate(preview_results, 1):
                    print(f"\n{i}. 【{result.get('type', '未知')}】")
                    print(f"   原文件名: {result['original_name']}")
                    print(f"   新文件名: {result['new_name']}")
                    
                    if result.get('has_api_data'):
                        print(f"   🌐 API数据: ✅ 已获取")
                        
                        if result.get('chinese_title'):
                            print(f"   中文标题: {result['chinese_title']}")
                        if result.get('original_title'):
                            print(f"   原始标题: {result['original_title']}")
                        
                        ratings = []
                        if result.get('tmdb_rating'):
                            ratings.append(f"TMDb: {result['tmdb_rating']:.1f}")
                        if result.get('douban_rating'):
                            ratings.append(f"豆瓣: {result['douban_rating']:.1f}")
                        if ratings:
                            print(f"   评分: {' | '.join(ratings)}")
                        
                        if result.get('genres'):
                            print(f"   类型: {', '.join(result['genres'])}")
                        if result.get('director'):
                            print(f"   导演: {result['director']}")
                    else:
                        print(f"   🌐 API数据: ❌ 未获取")
    
    def demo_performance_test(self) -> None:
        """
        演示性能测试
        """
        print("\n⚡ 增强版性能测试")
        print("=" * 60)
        
        # 创建测试文件名列表
        test_filenames = [
            "The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv",
            "Inception.2010.720p.WEBRip.x264.AAC-YTS.mp4",
            "流浪地球.2019.1080p.WEBRip.x264.mkv",
            "Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv",
            "Breaking.Bad.S01E01.720p.BluRay.x264-DEMAND.avi"
        ]
        
        print(f"测试文件数量: {len(test_filenames)}")
        
        # 测试基础信息提取性能
        print(f"\n🔍 基础信息提取性能测试...")
        start_time = time.time()
        
        basic_results = []
        for filename in test_filenames:
            basic_info = self.renamer.extract_video_info(filename)
            basic_results.append(basic_info)
        
        basic_time = time.time() - start_time
        print(f"   基础提取耗时: {basic_time:.2f} 秒")
        print(f"   平均每个文件: {(basic_time/len(test_filenames)*1000):.0f} 毫秒")
        
        # 测试增强信息提取性能（包含API调用）
        print(f"\n🌐 增强信息提取性能测试...")
        start_time = time.time()
        
        enhanced_results = []
        api_success_count = 0
        
        for filename in test_filenames:
            try:
                basic_info, api_metadata = self.renamer.extract_video_info_enhanced(filename)
                enhanced_results.append((basic_info, api_metadata))
                if api_metadata:
                    api_success_count += 1
            except Exception as e:
                print(f"   处理 {filename} 时出错: {e}")
                enhanced_results.append((None, None))
        
        enhanced_time = time.time() - start_time
        print(f"   增强提取耗时: {enhanced_time:.2f} 秒")
        print(f"   平均每个文件: {(enhanced_time/len(test_filenames)*1000):.0f} 毫秒")
        print(f"   API成功率: {api_success_count}/{len(test_filenames)} ({api_success_count/len(test_filenames)*100:.1f}%)")
        
        # 性能对比
        if basic_time > 0:
            slowdown = enhanced_time / basic_time
            print(f"   性能影响: 增强版比基础版慢 {slowdown:.1f} 倍")
        
        # 缓存效果测试
        print(f"\n💾 缓存效果测试...")
        start_time = time.time()
        
        cached_results = []
        for filename in test_filenames:
            try:
                basic_info, api_metadata = self.renamer.extract_video_info_enhanced(filename)
                cached_results.append((basic_info, api_metadata))
            except Exception as e:
                cached_results.append((None, None))
        
        cached_time = time.time() - start_time
        print(f"   缓存提取耗时: {cached_time:.2f} 秒")
        print(f"   平均每个文件: {(cached_time/len(test_filenames)*1000):.0f} 毫秒")
        
        if enhanced_time > 0:
            speedup = enhanced_time / cached_time
            print(f"   缓存加速: 比首次提取快 {speedup:.1f} 倍")
    
    def cleanup_demo_files(self) -> None:
        """
        清理演示文件
        """
        if self.demo_dir.exists():
            print(f"\n🧹 清理增强版演示文件...")
            shutil.rmtree(self.demo_dir)
            print(f"✅ 演示文件已清理: {self.demo_dir}")
        else:
            print(f"📁 演示目录不存在，无需清理")
    
    def run_all_demos(self) -> None:
        """
        运行所有增强版演示
        """
        print("🎬 智能影视文件重命名工具 - 增强版完整演示")
        print("=" * 80)
        
        try:
            # 1. 创建测试文件
            self.create_test_files()
            
            # 2. API连接演示
            self.demo_api_connections()
            
            # 3. 元数据提取演示
            self.demo_metadata_extraction()
            
            # 4. 增强模板演示
            self.demo_enhanced_templates()
            
            # 5. NFO文件生成演示
            self.demo_nfo_generation()
            
            # 6. 海报下载演示
            self.demo_poster_download()
            
            # 7. 增强预览演示
            self.demo_enhanced_preview()
            
            # 8. 性能测试
            self.demo_performance_test()
            
            print(f"\n🎉 所有增强版演示完成！")
            
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
        print("🎬 智能影视文件重命名工具 - 增强版演示菜单")
        
        while True:
            print(f"\n{'='*60}")
            print("请选择演示功能:")
            print("1. 创建测试文件")
            print("2. API连接演示")
            print("3. 元数据提取演示")
            print("4. 增强模板演示")
            print("5. NFO文件生成演示")
            print("6. 海报下载演示")
            print("7. 增强预览演示")
            print("8. 性能测试")
            print("9. 运行所有演示")
            print("10. 清理演示文件")
            print("11. 退出")
            print(f"{'='*60}")
            
            try:
                choice = input("请输入选择 (1-11): ").strip()
                
                if choice == '1':
                    self.create_test_files()
                elif choice == '2':
                    self.demo_api_connections()
                elif choice == '3':
                    self.demo_metadata_extraction()
                elif choice == '4':
                    self.demo_enhanced_templates()
                elif choice == '5':
                    self.demo_nfo_generation()
                elif choice == '6':
                    self.demo_poster_download()
                elif choice == '7':
                    self.demo_enhanced_preview()
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
    print("🎬 智能影视文件重命名工具 - 增强版演示程序")
    print("   作者: OpenHands AI")
    print("   功能: 演示API集成和元数据获取功能")
    
    # 创建演示实例
    demo = EnhancedVideoRenamerDemo()
    
    # 运行交互式演示
    demo.interactive_demo()


if __name__ == "__main__":
    main()