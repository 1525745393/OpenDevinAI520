#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能影视文件重命名工具
作者: OpenHands AI
版本: 1.0.0
描述: 跨平台影视文件智能重命名工具，支持群晖Video Station、Windows、macOS

功能特点:
1. 跨平台支持（群晖、Windows、macOS）
2. 智能提取影视信息（标题、年份、季集、分辨率等）
3. 灵活的重命名模板配置
4. Dry-run 模拟预览功能
5. 正则表达式自定义提取规则
6. 多种视频格式支持
7. 群晖Video Station优化
8. 详细的日志记录
9. 用户友好的交互界面
"""

import os
import sys
import re
import json
import logging
import platform
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import shutil


class VideoInfo:
    """
    视频信息类
    
    用于存储从文件名中提取的视频信息
    """
    
    def __init__(self):
        """初始化视频信息"""
        self.title = ""           # 影片标题
        self.year = ""            # 年份
        self.season = ""          # 季数
        self.episode = ""         # 集数
        self.resolution = ""      # 分辨率
        self.quality = ""         # 画质标识
        self.source = ""          # 来源标识
        self.codec = ""           # 编码格式
        self.audio = ""           # 音频格式
        self.language = ""        # 语言标识
        self.group = ""           # 制作组
        self.extension = ""       # 文件扩展名
        self.original_name = ""   # 原始文件名
        self.is_movie = True      # 是否为电影（False为电视剧）
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式"""
        return {
            'title': self.title,
            'year': self.year,
            'season': self.season,
            'episode': self.episode,
            'resolution': self.resolution,
            'quality': self.quality,
            'source': self.source,
            'codec': self.codec,
            'audio': self.audio,
            'language': self.language,
            'group': self.group,
            'extension': self.extension,
            'original_name': self.original_name,
            'is_movie': self.is_movie
        }


class VideoRenamer:
    """
    视频文件重命名工具主类
    
    包含所有核心功能：
    - 配置管理
    - 文件名解析
    - 重命名逻辑
    - 跨平台支持
    """
    
    def __init__(self):
        """初始化重命名工具"""
        # 获取脚本所在目录
        self.script_dir = Path(__file__).parent.absolute()
        
        # 配置文件路径
        self.config_file = self.script_dir / "video_renamer_config.json"
        
        # 日志文件路径
        self.log_dir = self.script_dir / "logs"
        self.log_file = self.log_dir / "video_renamer.log"
        
        # 配置字典
        self.config: Dict[str, Any] = {}
        
        # 检测操作系统
        self.os_type = platform.system().lower()
        
        # 初始化日志系统
        self._setup_logging()
        
        # 记录启动信息
        self.logger.info("=" * 60)
        self.logger.info("智能影视文件重命名工具启动")
        self.logger.info(f"操作系统: {platform.system()} {platform.release()}")
        self.logger.info(f"Python版本: {platform.python_version()}")
        self.logger.info(f"脚本路径: {self.script_dir}")
        self.logger.info("=" * 60)
    
    def _setup_logging(self) -> None:
        """
        设置日志系统
        
        配置日志格式和输出方式
        """
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 配置日志记录器
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"日志系统初始化完成，日志文件: {self.log_file}")
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        创建默认配置
        
        返回:
            Dict[str, Any]: 包含所有默认配置的字典
        """
        return {
            # 应用基本信息
            "app_info": {
                "name": "智能影视文件重命名工具",
                "version": "1.0.0",
                "description": "跨平台影视文件智能重命名工具",
                "author": "OpenHands AI",
                "created_time": datetime.datetime.now().isoformat(),
                "supported_os": ["Windows", "macOS", "Linux", "Synology"]
            },
            
            # 支持的视频格式
            "supported_formats": {
                "video_extensions": [
                    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", 
                    ".webm", ".m4v", ".3gp", ".ts", ".mts", ".m2ts",
                    ".rmvb", ".rm", ".asf", ".f4v", ".vob"
                ],
                "subtitle_extensions": [
                    ".srt", ".ass", ".ssa", ".sub", ".idx", ".vtt"
                ]
            },
            
            # 重命名模板配置
            "naming_templates": {
                # 电影命名模板
                "movie_templates": {
                    "synology_default": "{title} ({year}) [{resolution}] [{quality}].{ext}",
                    "plex_format": "{title} ({year}).{ext}",
                    "detailed": "{title} ({year}) [{resolution}] [{source}] [{codec}] [{audio}].{ext}",
                    "simple": "{title} ({year}).{ext}",
                    "custom": "{title} ({year}) - {quality}.{ext}"
                },
                
                # 电视剧命名模板
                "tv_templates": {
                    "synology_default": "{title} S{season:02d}E{episode:02d} [{resolution}] [{quality}].{ext}",
                    "plex_format": "{title} - S{season:02d}E{episode:02d}.{ext}",
                    "detailed": "{title} S{season:02d}E{episode:02d} [{resolution}] [{source}] [{codec}].{ext}",
                    "simple": "{title} S{season:02d}E{episode:02d}.{ext}",
                    "custom": "{title} - 第{season}季第{episode}集.{ext}"
                },
                
                # 当前使用的模板
                "current_movie_template": "synology_default",
                "current_tv_template": "synology_default"
            },
            
            # 正则表达式提取规则
            "extraction_rules": {
                # 电影提取规则（按优先级排序）
                "movie_patterns": [
                    # 标准格式：电影名.年份.其他信息
                    {
                        "name": "标准电影格式",
                        "pattern": r"^(.+?)[\.\s]+(\d{4})[\.\s]*(.*)$",
                        "groups": {"title": 1, "year": 2, "extra": 3},
                        "description": "匹配：电影名.2023.1080p.BluRay.x264"
                    },
                    # 带括号年份：电影名 (2023) 其他信息
                    {
                        "name": "括号年份格式",
                        "pattern": r"^(.+?)\s*\((\d{4})\)\s*(.*)$",
                        "groups": {"title": 1, "year": 2, "extra": 3},
                        "description": "匹配：电影名 (2023) 1080p"
                    },
                    # 中文格式：电影名.2023.其他
                    {
                        "name": "中文电影格式",
                        "pattern": r"^(.+?)[\.\s]*(\d{4})[\.\s]*(.*)$",
                        "groups": {"title": 1, "year": 2, "extra": 3},
                        "description": "匹配中文电影名"
                    }
                ],
                
                # 电视剧提取规则
                "tv_patterns": [
                    # 标准格式：剧名.S01E01.其他信息
                    {
                        "name": "标准剧集格式",
                        "pattern": r"^(.+?)[\.\s]+[Ss](\d{1,2})[Ee](\d{1,2})[\.\s]*(.*)$",
                        "groups": {"title": 1, "season": 2, "episode": 3, "extra": 4},
                        "description": "匹配：剧名.S01E01.1080p"
                    },
                    # 数字格式：剧名.1x01.其他信息
                    {
                        "name": "数字季集格式",
                        "pattern": r"^(.+?)[\.\s]+(\d{1,2})x(\d{1,2})[\.\s]*(.*)$",
                        "groups": {"title": 1, "season": 2, "episode": 3, "extra": 4},
                        "description": "匹配：剧名.1x01.720p"
                    },
                    # 中文格式：剧名.第1季.第01集
                    {
                        "name": "中文季集格式",
                        "pattern": r"^(.+?)[\.\s]*第(\d{1,2})季[\.\s]*第(\d{1,2})集[\.\s]*(.*)$",
                        "groups": {"title": 1, "season": 2, "episode": 3, "extra": 4},
                        "description": "匹配中文季集格式"
                    }
                ],
                
                # 额外信息提取规则
                "extra_patterns": {
                    "resolution": [
                        r"(4K|2160p|1080p|720p|480p|360p)",
                        r"(\d{3,4}p)"
                    ],
                    "quality": [
                        r"(BluRay|BDRip|DVDRip|WEBRip|HDTV|CAM|TS|TC)",
                        r"(蓝光|高清|超清|标清)"
                    ],
                    "source": [
                        r"(Netflix|Amazon|Disney|HBO|Hulu|Apple)",
                        r"(网飞|亚马逊|迪士尼|爱奇艺|腾讯|优酷)"
                    ],
                    "codec": [
                        r"(x264|x265|H\.264|H\.265|HEVC|AVC)",
                        r"(h264|h265|hevc|avc)"
                    ],
                    "audio": [
                        r"(DTS|AC3|AAC|MP3|FLAC|Atmos)",
                        r"(杜比|环绕声)"
                    ],
                    "language": [
                        r"(Chinese|English|Japanese|Korean)",
                        r"(中文|英文|日文|韩文|国语|粤语)"
                    ],
                    "group": [
                        r"\[([^\]]+)\]$",  # 结尾的制作组标识
                        r"-([A-Za-z0-9]+)$"  # 结尾的组名
                    ]
                }
            },
            
            # 应用设置
            "app_settings": {
                "default_work_directory": "",  # 默认工作目录（空表示当前目录）
                "backup_enabled": True,        # 是否启用备份
                "backup_directory": "backup",  # 备份目录名
                "dry_run_default": True,       # 默认启用预览模式
                "auto_detect_type": True,      # 自动检测电影/电视剧类型
                "case_sensitive": False,       # 文件名大小写敏感
                "skip_existing": True,         # 跳过已存在的文件
                "create_directories": True,    # 自动创建目录
                "log_level": "INFO",          # 日志级别
                "max_log_files": 10,          # 最大日志文件数
                "encoding": "utf-8"           # 文件编码
            },
            
            # 群晖Video Station特殊配置
            "synology_settings": {
                "video_station_path": "/volume1/video",  # Video Station路径
                "movie_folder": "Movies",                # 电影文件夹
                "tv_folder": "TV Shows",                 # 电视剧文件夹
                "create_season_folders": True,           # 为电视剧创建季度文件夹
                "season_folder_format": "Season {season:02d}",  # 季度文件夹格式
                "metadata_files": [".nfo", ".jpg", ".png"],     # 元数据文件扩展名
                "preserve_metadata": True                # 保留元数据文件
            },
            
            # 安全设置
            "safety_settings": {
                "max_files_per_batch": 1000,    # 单次处理最大文件数
                "confirm_before_rename": True,   # 重命名前确认
                "create_undo_log": True,         # 创建撤销日志
                "forbidden_characters": ["<", ">", ":", "\"", "|", "?", "*"],  # 禁用字符
                "max_filename_length": 255,      # 最大文件名长度
                "preserve_original_case": False  # 保留原始大小写
            }
        }
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        返回:
            bool: 加载成功返回True，失败返回False
        """
        try:
            if not self.config_file.exists():
                self.logger.warning("配置文件不存在，将创建新的配置文件")
                return self._create_config_file()
            
            self.logger.info(f"正在加载配置文件: {self.config_file}")
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            if not self._validate_config():
                self.logger.warning("配置文件不完整，将重新创建")
                return self._create_config_file()
            
            self.logger.info("配置文件加载成功")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            self.logger.info("将创建新的配置文件")
            return self._create_config_file()
            
        except Exception as e:
            self.logger.error(f"加载配置文件时发生错误: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """
        验证配置文件完整性
        
        返回:
            bool: 配置完整返回True，否则返回False
        """
        required_sections = [
            "app_info", "supported_formats", "naming_templates",
            "extraction_rules", "app_settings", "synology_settings", "safety_settings"
        ]
        
        for section in required_sections:
            if section not in self.config:
                self.logger.warning(f"配置文件缺少必需的配置节: {section}")
                return False
        
        return True
    
    def _create_config_file(self) -> bool:
        """
        创建新的配置文件
        
        返回:
            bool: 创建成功返回True，失败返回False
        """
        try:
            self.logger.info("正在创建新的配置文件...")
            
            self.config = self._create_default_config()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"配置文件创建成功: {self.config_file}")
            self._show_config_created_message()
            
            return True
            
        except Exception as e:
            self.logger.error(f"创建配置文件时发生错误: {e}")
            return False
    
    def _show_config_created_message(self) -> None:
        """显示配置文件创建成功的提示信息"""
        print("\n" + "=" * 70)
        print("🎉 智能影视文件重命名工具配置文件创建成功！")
        print("=" * 70)
        print(f"📁 配置文件位置: {self.config_file}")
        print(f"📝 日志文件位置: {self.log_file}")
        print(f"💻 当前操作系统: {platform.system()}")
        print("\n📋 主要功能:")
        print("   • 智能提取影视信息（标题、年份、季集等）")
        print("   • 支持多种重命名模板")
        print("   • Dry-run 预览功能")
        print("   • 跨平台支持（Windows、macOS、群晖）")
        print("   • 群晖Video Station优化")
        print("\n⚙️ 配置说明:")
        print("   • naming_templates: 重命名模板设置")
        print("   • extraction_rules: 信息提取规则")
        print("   • synology_settings: 群晖专用设置")
        print("   • safety_settings: 安全保护设置")
        print("\n💡 使用提示:")
        print("   1. 首次使用建议启用 dry-run 模式预览")
        print("   2. 可以自定义正则表达式提取规则")
        print("   3. 支持批量处理和撤销操作")
        print("   4. 群晖用户可使用Video Station优化模板")
        print("=" * 70)
        print()
    
    def extract_video_info(self, filename: str) -> VideoInfo:
        """
        从文件名提取视频信息
        
        参数:
            filename (str): 文件名
        
        返回:
            VideoInfo: 提取的视频信息对象
        """
        info = VideoInfo()
        info.original_name = filename
        
        # 分离文件名和扩展名
        name_without_ext = Path(filename).stem
        info.extension = Path(filename).suffix.lower()
        
        self.logger.debug(f"开始解析文件名: {filename}")
        
        # 首先尝试电视剧模式
        tv_info = self._extract_tv_info(name_without_ext)
        if tv_info:
            info.title = tv_info.get('title', '')
            info.season = tv_info.get('season', '')
            info.episode = tv_info.get('episode', '')
            info.is_movie = False
            extra_info = tv_info.get('extra', '')
        else:
            # 尝试电影模式
            movie_info = self._extract_movie_info(name_without_ext)
            if movie_info:
                info.title = movie_info.get('title', '')
                info.year = movie_info.get('year', '')
                info.is_movie = True
                extra_info = movie_info.get('extra', '')
            else:
                # 无法识别，使用原文件名作为标题
                info.title = name_without_ext
                extra_info = ''
        
        # 提取额外信息（分辨率、画质等）
        if extra_info:
            self._extract_extra_info(extra_info, info)
        
        # 清理标题
        info.title = self._clean_title(info.title)
        
        self.logger.debug(f"解析结果: {info.to_dict()}")
        return info
    
    def _extract_tv_info(self, filename: str) -> Optional[Dict[str, str]]:
        """
        提取电视剧信息
        
        参数:
            filename (str): 文件名（不含扩展名）
        
        返回:
            Optional[Dict[str, str]]: 提取的信息字典，失败返回None
        """
        tv_patterns = self.config.get('extraction_rules', {}).get('tv_patterns', [])
        
        for pattern_config in tv_patterns:
            pattern = pattern_config.get('pattern', '')
            groups = pattern_config.get('groups', {})
            
            try:
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    result = {}
                    for key, group_num in groups.items():
                        if group_num <= len(match.groups()):
                            result[key] = match.group(group_num).strip()
                    
                    self.logger.debug(f"匹配电视剧模式: {pattern_config.get('name', '')}")
                    return result
                    
            except re.error as e:
                self.logger.warning(f"正则表达式错误: {pattern} - {e}")
                continue
        
        return None
    
    def _extract_movie_info(self, filename: str) -> Optional[Dict[str, str]]:
        """
        提取电影信息
        
        参数:
            filename (str): 文件名（不含扩展名）
        
        返回:
            Optional[Dict[str, str]]: 提取的信息字典，失败返回None
        """
        movie_patterns = self.config.get('extraction_rules', {}).get('movie_patterns', [])
        
        for pattern_config in movie_patterns:
            pattern = pattern_config.get('pattern', '')
            groups = pattern_config.get('groups', {})
            
            try:
                match = re.search(pattern, filename, re.IGNORECASE)
                if match:
                    result = {}
                    for key, group_num in groups.items():
                        if group_num <= len(match.groups()):
                            result[key] = match.group(group_num).strip()
                    
                    self.logger.debug(f"匹配电影模式: {pattern_config.get('name', '')}")
                    return result
                    
            except re.error as e:
                self.logger.warning(f"正则表达式错误: {pattern} - {e}")
                continue
        
        return None
    
    def _extract_extra_info(self, extra_text: str, info: VideoInfo) -> None:
        """
        从额外文本中提取详细信息
        
        参数:
            extra_text (str): 额外信息文本
            info (VideoInfo): 要更新的视频信息对象
        """
        extra_patterns = self.config.get('extraction_rules', {}).get('extra_patterns', {})
        
        for info_type, patterns in extra_patterns.items():
            for pattern in patterns:
                try:
                    match = re.search(pattern, extra_text, re.IGNORECASE)
                    if match:
                        value = match.group(1) if match.groups() else match.group(0)
                        setattr(info, info_type, value)
                        self.logger.debug(f"提取{info_type}: {value}")
                        break
                except re.error as e:
                    self.logger.warning(f"正则表达式错误: {pattern} - {e}")
                    continue
    
    def _clean_title(self, title: str) -> str:
        """
        清理标题文本
        
        参数:
            title (str): 原始标题
        
        返回:
            str: 清理后的标题
        """
        if not title:
            return title
        
        # 移除常见的分隔符
        title = re.sub(r'[\.\-_]+', ' ', title)
        
        # 移除多余的空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 移除禁用字符
        forbidden_chars = self.config.get('safety_settings', {}).get('forbidden_characters', [])
        for char in forbidden_chars:
            title = title.replace(char, '')
        
        return title
    
    def generate_new_filename(self, info: VideoInfo) -> str:
        """
        根据模板生成新文件名
        
        参数:
            info (VideoInfo): 视频信息对象
        
        返回:
            str: 生成的新文件名
        """
        templates = self.config.get('naming_templates', {})
        
        if info.is_movie:
            # 电影模板
            template_name = templates.get('current_movie_template', 'synology_default')
            template = templates.get('movie_templates', {}).get(template_name, '')
        else:
            # 电视剧模板
            template_name = templates.get('current_tv_template', 'synology_default')
            template = templates.get('tv_templates', {}).get(template_name, '')
        
        if not template:
            self.logger.warning(f"未找到模板: {template_name}")
            return info.original_name
        
        try:
            # 准备模板变量
            template_vars = {
                'title': info.title or 'Unknown',
                'year': info.year or '',
                'season': int(info.season) if info.season.isdigit() else 1,
                'episode': int(info.episode) if info.episode.isdigit() else 1,
                'resolution': info.resolution or '',
                'quality': info.quality or '',
                'source': info.source or '',
                'codec': info.codec or '',
                'audio': info.audio or '',
                'language': info.language or '',
                'group': info.group or '',
                'ext': info.extension.lstrip('.')
            }
            
            # 应用模板
            new_name = template.format(**template_vars)
            
            # 清理文件名
            new_name = self._sanitize_filename(new_name)
            
            self.logger.debug(f"生成新文件名: {new_name}")
            return new_name
            
        except Exception as e:
            self.logger.error(f"生成文件名时发生错误: {e}")
            return info.original_name
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符
        
        参数:
            filename (str): 原始文件名
        
        返回:
            str: 清理后的文件名
        """
        # 移除禁用字符
        forbidden_chars = self.config.get('safety_settings', {}).get('forbidden_characters', [])
        for char in forbidden_chars:
            filename = filename.replace(char, '')
        
        # 移除多余的空格和点
        filename = re.sub(r'\s+', ' ', filename).strip()
        filename = re.sub(r'\.+', '.', filename)
        
        # 移除开头和结尾的点和空格
        filename = filename.strip('. ')
        
        # 检查文件名长度
        max_length = self.config.get('safety_settings', {}).get('max_filename_length', 255)
        if len(filename) > max_length:
            name_part = Path(filename).stem
            ext_part = Path(filename).suffix
            max_name_length = max_length - len(ext_part)
            filename = name_part[:max_name_length] + ext_part
        
        return filename
    
    def scan_directory(self, directory: str) -> List[str]:
        """
        扫描目录中的视频文件
        
        参数:
            directory (str): 目录路径
        
        返回:
            List[str]: 视频文件路径列表
        """
        video_files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            self.logger.error(f"目录不存在: {directory}")
            return video_files
        
        # 获取支持的视频格式
        supported_extensions = self.config.get('supported_formats', {}).get('video_extensions', [])
        
        try:
            # 递归扫描目录
            for file_path in directory_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    video_files.append(str(file_path))
            
            self.logger.info(f"在目录 {directory} 中找到 {len(video_files)} 个视频文件")
            
        except Exception as e:
            self.logger.error(f"扫描目录时发生错误: {e}")
        
        return video_files
    
    def preview_rename(self, file_paths: List[str]) -> List[Dict[str, str]]:
        """
        预览重命名结果
        
        参数:
            file_paths (List[str]): 文件路径列表
        
        返回:
            List[Dict[str, str]]: 预览结果列表
        """
        preview_results = []
        
        for file_path in file_paths:
            try:
                file_path_obj = Path(file_path)
                filename = file_path_obj.name
                
                # 提取视频信息
                info = self.extract_video_info(filename)
                
                # 生成新文件名
                new_filename = self.generate_new_filename(info)
                
                # 构建新路径
                new_path = file_path_obj.parent / new_filename
                
                preview_results.append({
                    'original_path': str(file_path),
                    'original_name': filename,
                    'new_name': new_filename,
                    'new_path': str(new_path),
                    'type': '电影' if info.is_movie else '电视剧',
                    'title': info.title,
                    'year': info.year,
                    'season': info.season,
                    'episode': info.episode,
                    'resolution': info.resolution,
                    'quality': info.quality
                })
                
            except Exception as e:
                self.logger.error(f"预览文件 {file_path} 时发生错误: {e}")
                preview_results.append({
                    'original_path': str(file_path),
                    'original_name': Path(file_path).name,
                    'new_name': Path(file_path).name,
                    'new_path': str(file_path),
                    'type': '错误',
                    'error': str(e)
                })
        
        return preview_results
    
    def rename_files(self, file_paths: List[str], dry_run: bool = True) -> Dict[str, Any]:
        """
        执行文件重命名
        
        参数:
            file_paths (List[str]): 文件路径列表
            dry_run (bool): 是否为预览模式
        
        返回:
            Dict[str, Any]: 重命名结果统计
        """
        results = {
            'total': len(file_paths),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'renamed_files': []
        }
        
        # 安全检查
        max_files = self.config.get('safety_settings', {}).get('max_files_per_batch', 1000)
        if len(file_paths) > max_files:
            error_msg = f"文件数量超过安全限制 ({max_files})，请分批处理"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
        
        # 创建备份目录（如果启用）
        backup_enabled = self.config.get('app_settings', {}).get('backup_enabled', True)
        if backup_enabled and not dry_run:
            backup_dir = self._create_backup_directory()
        
        for file_path in file_paths:
            try:
                file_path_obj = Path(file_path)
                
                if not file_path_obj.exists():
                    self.logger.warning(f"文件不存在: {file_path}")
                    results['skipped'] += 1
                    continue
                
                # 提取信息并生成新文件名
                info = self.extract_video_info(file_path_obj.name)
                new_filename = self.generate_new_filename(info)
                new_path = file_path_obj.parent / new_filename
                
                # 检查是否需要重命名
                if file_path_obj.name == new_filename:
                    self.logger.info(f"文件名无需更改: {file_path_obj.name}")
                    results['skipped'] += 1
                    continue
                
                # 检查目标文件是否已存在
                if new_path.exists() and self.config.get('app_settings', {}).get('skip_existing', True):
                    self.logger.warning(f"目标文件已存在，跳过: {new_path}")
                    results['skipped'] += 1
                    continue
                
                if dry_run:
                    # 预览模式，只记录不执行
                    self.logger.info(f"[预览] {file_path_obj.name} -> {new_filename}")
                    results['success'] += 1
                else:
                    # 实际重命名
                    if backup_enabled:
                        # 创建备份
                        backup_path = backup_dir / file_path_obj.name
                        shutil.copy2(file_path_obj, backup_path)
                    
                    # 执行重命名
                    file_path_obj.rename(new_path)
                    
                    self.logger.info(f"重命名成功: {file_path_obj.name} -> {new_filename}")
                    results['success'] += 1
                    results['renamed_files'].append({
                        'original': str(file_path),
                        'new': str(new_path)
                    })
                
            except Exception as e:
                error_msg = f"处理文件 {file_path} 时发生错误: {e}"
                self.logger.error(error_msg)
                results['failed'] += 1
                results['errors'].append(error_msg)
        
        return results
    
    def _create_backup_directory(self) -> Path:
        """
        创建备份目录
        
        返回:
            Path: 备份目录路径
        """
        backup_name = self.config.get('app_settings', {}).get('backup_directory', 'backup')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.script_dir / f"{backup_name}_{timestamp}"
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"创建备份目录: {backup_dir}")
        
        return backup_dir
    
    def show_preview_table(self, preview_results: List[Dict[str, str]]) -> None:
        """
        显示预览结果表格
        
        参数:
            preview_results (List[Dict[str, str]]): 预览结果列表
        """
        if not preview_results:
            print("没有找到需要重命名的文件")
            return
        
        print(f"\n{'='*80}")
        print(f"📋 重命名预览结果 (共 {len(preview_results)} 个文件)")
        print(f"{'='*80}")
        
        for i, result in enumerate(preview_results, 1):
            print(f"\n{i:3d}. 【{result.get('type', '未知')}】")
            print(f"     原文件名: {result['original_name']}")
            print(f"     新文件名: {result['new_name']}")
            
            if result.get('title'):
                print(f"     标题: {result['title']}")
            if result.get('year'):
                print(f"     年份: {result['year']}")
            if result.get('season') and result.get('episode'):
                print(f"     季集: S{result['season']}E{result['episode']}")
            if result.get('resolution'):
                print(f"     分辨率: {result['resolution']}")
            if result.get('quality'):
                print(f"     画质: {result['quality']}")
            
            if result.get('error'):
                print(f"     ❌ 错误: {result['error']}")
        
        print(f"\n{'='*80}")
    
    def interactive_mode(self) -> None:
        """
        交互式模式主界面
        """
        print(f"\n🎬 智能影视文件重命名工具 v{self.config.get('app_info', {}).get('version', '1.0.0')}")
        print(f"   当前操作系统: {platform.system()}")
        print(f"   工作目录: {os.getcwd()}")
        
        while True:
            print(f"\n{'='*50}")
            print("请选择操作:")
            print("1. 扫描并预览重命名")
            print("2. 执行重命名（实际操作）")
            print("3. 查看配置信息")
            print("4. 修改配置")
            print("5. 帮助信息")
            print("6. 退出")
            print(f"{'='*50}")
            
            try:
                choice = input("请输入选择 (1-6): ").strip()
                
                if choice == '1':
                    self._handle_preview_mode()
                elif choice == '2':
                    self._handle_rename_mode()
                elif choice == '3':
                    self._show_config_info()
                elif choice == '4':
                    self._handle_config_modification()
                elif choice == '5':
                    self._show_help()
                elif choice == '6':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请输入 1-6")
                    
            except KeyboardInterrupt:
                print(f"\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                self.logger.error(f"交互模式错误: {e}")
    
    def _handle_preview_mode(self) -> None:
        """处理预览模式"""
        directory = input("请输入要扫描的目录路径 (回车使用当前目录): ").strip()
        if not directory:
            directory = os.getcwd()
        
        print(f"🔍 正在扫描目录: {directory}")
        file_paths = self.scan_directory(directory)
        
        if not file_paths:
            print("❌ 未找到视频文件")
            return
        
        print(f"✅ 找到 {len(file_paths)} 个视频文件")
        
        # 生成预览
        preview_results = self.preview_rename(file_paths)
        self.show_preview_table(preview_results)
    
    def _handle_rename_mode(self) -> None:
        """处理重命名模式"""
        directory = input("请输入要处理的目录路径 (回车使用当前目录): ").strip()
        if not directory:
            directory = os.getcwd()
        
        print(f"🔍 正在扫描目录: {directory}")
        file_paths = self.scan_directory(directory)
        
        if not file_paths:
            print("❌ 未找到视频文件")
            return
        
        print(f"✅ 找到 {len(file_paths)} 个视频文件")
        
        # 先显示预览
        preview_results = self.preview_rename(file_paths)
        self.show_preview_table(preview_results)
        
        # 确认执行
        confirm = input(f"\n⚠️  确定要重命名这 {len(file_paths)} 个文件吗？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        # 执行重命名
        print("🚀 开始重命名...")
        results = self.rename_files(file_paths, dry_run=False)
        
        # 显示结果
        print(f"\n📊 重命名完成:")
        print(f"   总文件数: {results['total']}")
        print(f"   成功: {results['success']}")
        print(f"   失败: {results['failed']}")
        print(f"   跳过: {results['skipped']}")
        
        if results['errors']:
            print(f"\n❌ 错误信息:")
            for error in results['errors']:
                print(f"   • {error}")
    
    def _show_config_info(self) -> None:
        """显示配置信息"""
        print(f"\n📋 当前配置信息:")
        print(f"   应用版本: {self.config.get('app_info', {}).get('version', '未知')}")
        print(f"   配置文件: {self.config_file}")
        
        # 显示当前模板
        templates = self.config.get('naming_templates', {})
        movie_template = templates.get('current_movie_template', '未设置')
        tv_template = templates.get('current_tv_template', '未设置')
        print(f"   电影模板: {movie_template}")
        print(f"   电视剧模板: {tv_template}")
        
        # 显示安全设置
        safety = self.config.get('safety_settings', {})
        print(f"   最大批处理文件数: {safety.get('max_files_per_batch', '未设置')}")
        print(f"   备份功能: {'启用' if self.config.get('app_settings', {}).get('backup_enabled', False) else '禁用'}")
    
    def _handle_config_modification(self) -> None:
        """处理配置修改"""
        print(f"\n⚙️ 配置修改选项:")
        print("1. 修改电影重命名模板")
        print("2. 修改电视剧重命名模板")
        print("3. 切换备份功能")
        print("4. 返回主菜单")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == '1':
            self._modify_movie_template()
        elif choice == '2':
            self._modify_tv_template()
        elif choice == '3':
            self._toggle_backup()
        elif choice == '4':
            return
        else:
            print("❌ 无效选择")
    
    def _modify_movie_template(self) -> None:
        """修改电影模板"""
        templates = self.config.get('naming_templates', {}).get('movie_templates', {})
        
        print(f"\n📽️ 可用的电影模板:")
        for i, (name, template) in enumerate(templates.items(), 1):
            print(f"{i}. {name}: {template}")
        
        try:
            choice = int(input("请选择模板编号: ")) - 1
            template_names = list(templates.keys())
            
            if 0 <= choice < len(template_names):
                selected_template = template_names[choice]
                self.config['naming_templates']['current_movie_template'] = selected_template
                
                # 保存配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                
                print(f"✅ 电影模板已更改为: {selected_template}")
            else:
                print("❌ 无效选择")
                
        except ValueError:
            print("❌ 请输入有效数字")
    
    def _modify_tv_template(self) -> None:
        """修改电视剧模板"""
        templates = self.config.get('naming_templates', {}).get('tv_templates', {})
        
        print(f"\n📺 可用的电视剧模板:")
        for i, (name, template) in enumerate(templates.items(), 1):
            print(f"{i}. {name}: {template}")
        
        try:
            choice = int(input("请选择模板编号: ")) - 1
            template_names = list(templates.keys())
            
            if 0 <= choice < len(template_names):
                selected_template = template_names[choice]
                self.config['naming_templates']['current_tv_template'] = selected_template
                
                # 保存配置
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                
                print(f"✅ 电视剧模板已更改为: {selected_template}")
            else:
                print("❌ 无效选择")
                
        except ValueError:
            print("❌ 请输入有效数字")
    
    def _toggle_backup(self) -> None:
        """切换备份功能"""
        current_state = self.config.get('app_settings', {}).get('backup_enabled', True)
        new_state = not current_state
        
        self.config['app_settings']['backup_enabled'] = new_state
        
        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 备份功能已{'启用' if new_state else '禁用'}")
    
    def _show_help(self) -> None:
        """显示帮助信息"""
        print(f"\n📖 帮助信息:")
        print(f"{'='*60}")
        print("🎯 功能说明:")
        print("   • 智能提取影视文件信息（标题、年份、季集等）")
        print("   • 支持多种重命名模板")
        print("   • 预览模式避免误操作")
        print("   • 自动备份原文件")
        print("   • 跨平台支持")
        
        print(f"\n📝 支持的文件格式:")
        formats = self.config.get('supported_formats', {}).get('video_extensions', [])
        print(f"   {', '.join(formats)}")
        
        print(f"\n🔧 模板变量说明:")
        print("   {title} - 影片标题")
        print("   {year} - 年份")
        print("   {season} - 季数")
        print("   {episode} - 集数")
        print("   {resolution} - 分辨率")
        print("   {quality} - 画质")
        print("   {ext} - 文件扩展名")
        
        print(f"\n💡 使用建议:")
        print("   1. 首次使用建议先预览结果")
        print("   2. 重要文件建议启用备份功能")
        print("   3. 可以自定义正则表达式规则")
        print("   4. 群晖用户推荐使用Video Station模板")
        print(f"{'='*60}")
    
    def run(self) -> None:
        """
        运行主程序
        """
        try:
            # 加载配置
            if not self.load_config():
                print("❌ 配置加载失败，程序无法继续运行")
                return
            
            # 启动交互模式
            self.interactive_mode()
            
        except Exception as e:
            self.logger.error(f"程序运行失败: {e}")
            print(f"❌ 程序运行失败: {e}")
        
        finally:
            self.logger.info("智能影视文件重命名工具结束")


def main():
    """
    程序主函数
    """
    print("🎬 智能影视文件重命名工具")
    print("   支持平台: Windows、macOS、群晖NAS")
    print("   作者: OpenHands AI")
    
    # 创建应用实例
    renamer = VideoRenamer()
    
    # 运行应用
    renamer.run()


# 程序入口点
if __name__ == "__main__":
    main()