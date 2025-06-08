"""
影视文件重命名工具
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from src.utils.logger import setup_logger
from src.utils.file_utils import FileUtils

class MediaRenamer:
    """影视文件重命名工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化影视文件重命名工具
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = setup_logger("MediaRenamer")
        self.file_utils = FileUtils()
        
        # 视频文件扩展名
        self.video_extensions = {
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm',
            '.m4v', '.3gp', '.ts', '.mts', '.m2ts', '.vob', '.rmvb'
        }
        
        # 常见的无用词汇
        self.junk_words = {
            'hdtv', 'web-dl', 'webrip', 'bluray', 'brrip', 'dvdrip',
            'x264', 'x265', 'h264', 'h265', 'aac', 'ac3', 'dts',
            '720p', '1080p', '2160p', '4k', 'uhd', 'hdr', 'sdr',
            'proper', 'repack', 'internal', 'limited', 'unrated',
            'extended', 'directors', 'cut', 'imax', 'remux'
        }
        
        # 电视剧季集模式
        self.tv_patterns = [
            r'[Ss](\d{1,2})[Ee](\d{1,3})',  # S01E01
            r'[Ss](\d{1,2})\.?[Ee](\d{1,3})',  # S01.E01
            r'(\d{1,2})x(\d{1,3})',  # 1x01
            r'[Ss]eason[\s\.]?(\d{1,2})[\s\.]?[Ee]pisode[\s\.]?(\d{1,3})',  # Season 1 Episode 1
        ]
        
        # 年份模式
        self.year_pattern = r'\b(19\d{2}|20\d{2})\b'
        
        # 分辨率模式
        self.resolution_pattern = r'\b(480p|720p|1080p|2160p|4k)\b'
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "影视文件重命名工具 - 智能识别并重命名电影、电视剧文件"
    
    def execute(self, action: str, args: List[str]) -> Optional[str]:
        """
        执行工具操作
        
        Args:
            action: 操作名称
            args: 参数列表
            
        Returns:
            Optional[str]: 执行结果
        """
        if action == "rename_movies":
            return self._rename_movies(args)
        elif action == "rename_tv_shows":
            return self._rename_tv_shows(args)
        elif action == "auto_rename":
            return self._auto_rename(args)
        elif action == "analyze":
            return self._analyze_files(args)
        elif action == "organize":
            return self._organize_media(args)
        elif action == "help":
            return self._show_help()
        else:
            return f"未知操作: {action}"
    
    def _rename_movies(self, args: List[str]) -> str:
        """
        重命名电影文件
        
        Args:
            args: 参数列表 [directory, pattern]
            
        Returns:
            str: 重命名结果
        """
        if not args:
            return "请指定目录路径"
        
        directory = Path(args[0])
        pattern = args[1] if len(args) > 1 else "{title} ({year})"
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        renamed_count = 0
        error_count = 0
        
        try:
            video_files = self._find_video_files(directory)
            
            for file_path in video_files:
                try:
                    movie_info = self._extract_movie_info(file_path.stem)
                    
                    if movie_info['title']:
                        new_name = self._format_movie_name(movie_info, pattern)
                        new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                        
                        if new_path != file_path and not new_path.exists():
                            file_path.rename(new_path)
                            self.logger.info(f"重命名电影: {file_path.name} -> {new_path.name}")
                            renamed_count += 1
                        else:
                            self.logger.warning(f"跳过文件: {file_path.name} (目标文件已存在或名称相同)")
                    else:
                        self.logger.warning(f"无法识别电影信息: {file_path.name}")
                        error_count += 1
                
                except Exception as e:
                    self.logger.error(f"重命名失败 {file_path}: {e}")
                    error_count += 1
            
            return f"电影重命名完成: {renamed_count} 个文件成功, {error_count} 个文件失败"
        
        except Exception as e:
            return f"电影重命名失败: {e}"
    
    def _rename_tv_shows(self, args: List[str]) -> str:
        """
        重命名电视剧文件
        
        Args:
            args: 参数列表 [directory, pattern]
            
        Returns:
            str: 重命名结果
        """
        if not args:
            return "请指定目录路径"
        
        directory = Path(args[0])
        pattern = args[1] if len(args) > 1 else "{title} S{season:02d}E{episode:02d}"
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        renamed_count = 0
        error_count = 0
        
        try:
            video_files = self._find_video_files(directory)
            
            for file_path in video_files:
                try:
                    tv_info = self._extract_tv_info(file_path.stem)
                    
                    if tv_info['title'] and tv_info['season'] and tv_info['episode']:
                        new_name = self._format_tv_name(tv_info, pattern)
                        new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                        
                        if new_path != file_path and not new_path.exists():
                            file_path.rename(new_path)
                            self.logger.info(f"重命名电视剧: {file_path.name} -> {new_path.name}")
                            renamed_count += 1
                        else:
                            self.logger.warning(f"跳过文件: {file_path.name} (目标文件已存在或名称相同)")
                    else:
                        self.logger.warning(f"无法识别电视剧信息: {file_path.name}")
                        error_count += 1
                
                except Exception as e:
                    self.logger.error(f"重命名失败 {file_path}: {e}")
                    error_count += 1
            
            return f"电视剧重命名完成: {renamed_count} 个文件成功, {error_count} 个文件失败"
        
        except Exception as e:
            return f"电视剧重命名失败: {e}"
    
    def _auto_rename(self, args: List[str]) -> str:
        """
        自动识别并重命名影视文件
        
        Args:
            args: 参数列表 [directory]
            
        Returns:
            str: 重命名结果
        """
        if not args:
            return "请指定目录路径"
        
        directory = Path(args[0])
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        movie_count = 0
        tv_count = 0
        error_count = 0
        
        try:
            video_files = self._find_video_files(directory)
            
            for file_path in video_files:
                try:
                    # 先尝试识别为电视剧
                    tv_info = self._extract_tv_info(file_path.stem)
                    
                    if tv_info['title'] and tv_info['season'] and tv_info['episode']:
                        # 识别为电视剧
                        new_name = self._format_tv_name(tv_info, "{title} S{season:02d}E{episode:02d}")
                        new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                        
                        if new_path != file_path and not new_path.exists():
                            file_path.rename(new_path)
                            self.logger.info(f"重命名电视剧: {file_path.name} -> {new_path.name}")
                            tv_count += 1
                    else:
                        # 尝试识别为电影
                        movie_info = self._extract_movie_info(file_path.stem)
                        
                        if movie_info['title']:
                            new_name = self._format_movie_name(movie_info, "{title} ({year})")
                            new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                            
                            if new_path != file_path and not new_path.exists():
                                file_path.rename(new_path)
                                self.logger.info(f"重命名电影: {file_path.name} -> {new_path.name}")
                                movie_count += 1
                        else:
                            self.logger.warning(f"无法识别文件类型: {file_path.name}")
                            error_count += 1
                
                except Exception as e:
                    self.logger.error(f"重命名失败 {file_path}: {e}")
                    error_count += 1
            
            return f"自动重命名完成: {movie_count} 个电影, {tv_count} 个电视剧, {error_count} 个失败"
        
        except Exception as e:
            return f"自动重命名失败: {e}"
    
    def _analyze_files(self, args: List[str]) -> str:
        """
        分析影视文件信息
        
        Args:
            args: 参数列表 [directory]
            
        Returns:
            str: 分析结果
        """
        if not args:
            return "请指定目录路径"
        
        directory = Path(args[0])
        
        if not directory.exists():
            return f"目录不存在: {directory}"
        
        try:
            video_files = self._find_video_files(directory)
            
            if not video_files:
                return "未找到视频文件"
            
            result = f"📁 目录: {directory}\n"
            result += f"🎬 视频文件总数: {len(video_files)}\n\n"
            
            movies = []
            tv_shows = []
            unknown = []
            
            for file_path in video_files:
                # 尝试识别为电视剧
                tv_info = self._extract_tv_info(file_path.stem)
                
                if tv_info['title'] and tv_info['season'] and tv_info['episode']:
                    tv_shows.append((file_path, tv_info))
                else:
                    # 尝试识别为电影
                    movie_info = self._extract_movie_info(file_path.stem)
                    
                    if movie_info['title']:
                        movies.append((file_path, movie_info))
                    else:
                        unknown.append(file_path)
            
            # 电影分析
            if movies:
                result += f"🎭 电影 ({len(movies)} 个):\n"
                for file_path, info in movies:
                    result += f"  📄 {file_path.name}\n"
                    result += f"     标题: {info['title']}\n"
                    if info['year']:
                        result += f"     年份: {info['year']}\n"
                    if info['resolution']:
                        result += f"     分辨率: {info['resolution']}\n"
                    result += "\n"
            
            # 电视剧分析
            if tv_shows:
                result += f"📺 电视剧 ({len(tv_shows)} 个):\n"
                for file_path, info in tv_shows:
                    result += f"  📄 {file_path.name}\n"
                    result += f"     标题: {info['title']}\n"
                    result += f"     季: {info['season']}, 集: {info['episode']}\n"
                    if info['year']:
                        result += f"     年份: {info['year']}\n"
                    if info['resolution']:
                        result += f"     分辨率: {info['resolution']}\n"
                    result += "\n"
            
            # 未识别文件
            if unknown:
                result += f"❓ 未识别 ({len(unknown)} 个):\n"
                for file_path in unknown:
                    result += f"  📄 {file_path.name}\n"
            
            return result
        
        except Exception as e:
            return f"分析失败: {e}"
    
    def _organize_media(self, args: List[str]) -> str:
        """
        组织影视文件到不同目录
        
        Args:
            args: 参数列表 [source_directory, target_directory]
            
        Returns:
            str: 组织结果
        """
        if len(args) < 2:
            return "参数不足。用法: organize <源目录> <目标目录>"
        
        source_dir = Path(args[0])
        target_dir = Path(args[1])
        
        if not source_dir.exists():
            return f"源目录不存在: {source_dir}"
        
        # 创建目标目录结构
        movies_dir = target_dir / "Movies"
        tv_shows_dir = target_dir / "TV Shows"
        unknown_dir = target_dir / "Unknown"
        
        self.file_utils.ensure_dir(movies_dir)
        self.file_utils.ensure_dir(tv_shows_dir)
        self.file_utils.ensure_dir(unknown_dir)
        
        moved_movies = 0
        moved_tv = 0
        moved_unknown = 0
        error_count = 0
        
        try:
            video_files = self._find_video_files(source_dir)
            
            for file_path in video_files:
                try:
                    # 尝试识别为电视剧
                    tv_info = self._extract_tv_info(file_path.stem)
                    
                    if tv_info['title'] and tv_info['season'] and tv_info['episode']:
                        # 电视剧：创建剧集目录
                        show_dir = tv_shows_dir / self._clean_filename(tv_info['title'])
                        season_dir = show_dir / f"Season {tv_info['season']:02d}"
                        self.file_utils.ensure_dir(season_dir)
                        
                        new_name = self._format_tv_name(tv_info, "{title} S{season:02d}E{episode:02d}")
                        target_path = season_dir / f"{new_name}{file_path.suffix}"
                        
                        if self.file_utils.move_file(file_path, target_path):
                            self.logger.info(f"移动电视剧: {file_path.name} -> {target_path}")
                            moved_tv += 1
                        else:
                            error_count += 1
                    else:
                        # 尝试识别为电影
                        movie_info = self._extract_movie_info(file_path.stem)
                        
                        if movie_info['title']:
                            new_name = self._format_movie_name(movie_info, "{title} ({year})")
                            target_path = movies_dir / f"{new_name}{file_path.suffix}"
                            
                            if self.file_utils.move_file(file_path, target_path):
                                self.logger.info(f"移动电影: {file_path.name} -> {target_path}")
                                moved_movies += 1
                            else:
                                error_count += 1
                        else:
                            # 未识别文件
                            target_path = unknown_dir / file_path.name
                            
                            if self.file_utils.move_file(file_path, target_path):
                                self.logger.info(f"移动未识别文件: {file_path.name} -> {target_path}")
                                moved_unknown += 1
                            else:
                                error_count += 1
                
                except Exception as e:
                    self.logger.error(f"移动文件失败 {file_path}: {e}")
                    error_count += 1
            
            return f"""
📁 影视文件组织完成:
电影: {moved_movies} 个
电视剧: {moved_tv} 个
未识别: {moved_unknown} 个
失败: {error_count} 个
"""
        
        except Exception as e:
            return f"组织文件失败: {e}"
    
    def _find_video_files(self, directory: Path) -> List[Path]:
        """
        查找视频文件
        
        Args:
            directory: 搜索目录
            
        Returns:
            List[Path]: 视频文件列表
        """
        video_files = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.video_extensions:
                video_files.append(file_path)
        
        return video_files
    
    def _extract_movie_info(self, filename: str) -> Dict[str, Any]:
        """
        从文件名提取电影信息
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 电影信息
        """
        info = {
            'title': '',
            'year': '',
            'resolution': '',
            'original': filename
        }
        
        # 清理文件名
        clean_name = self._clean_filename(filename)
        
        # 提取年份
        year_match = re.search(self.year_pattern, clean_name)
        if year_match:
            info['year'] = year_match.group(1)
            # 移除年份后的部分作为标题
            title_part = clean_name[:year_match.start()].strip()
        else:
            # 没有年份，尝试其他方式分割
            title_part = self._extract_title_part(clean_name)
        
        # 提取分辨率
        resolution_match = re.search(self.resolution_pattern, clean_name, re.IGNORECASE)
        if resolution_match:
            info['resolution'] = resolution_match.group(1)
        
        # 清理标题
        info['title'] = self._clean_title(title_part)
        
        return info
    
    def _extract_tv_info(self, filename: str) -> Dict[str, Any]:
        """
        从文件名提取电视剧信息
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 电视剧信息
        """
        info = {
            'title': '',
            'season': '',
            'episode': '',
            'year': '',
            'resolution': '',
            'original': filename
        }
        
        # 清理文件名
        clean_name = self._clean_filename(filename)
        
        # 尝试匹配季集信息
        for pattern in self.tv_patterns:
            match = re.search(pattern, clean_name, re.IGNORECASE)
            if match:
                info['season'] = int(match.group(1))
                info['episode'] = int(match.group(2))
                
                # 提取标题（季集信息之前的部分）
                title_part = clean_name[:match.start()].strip()
                break
        
        if not info['season']:
            return info  # 没有找到季集信息，不是电视剧
        
        # 提取年份
        year_match = re.search(self.year_pattern, clean_name)
        if year_match:
            info['year'] = year_match.group(1)
        
        # 提取分辨率
        resolution_match = re.search(self.resolution_pattern, clean_name, re.IGNORECASE)
        if resolution_match:
            info['resolution'] = resolution_match.group(1)
        
        # 清理标题
        info['title'] = self._clean_title(title_part)
        
        return info
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除常见的分隔符和替换为空格
        clean = re.sub(r'[._\-\[\]()]', ' ', filename)
        
        # 移除无用词汇
        words = clean.split()
        filtered_words = []
        
        for word in words:
            if word.lower() not in self.junk_words:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def _extract_title_part(self, clean_name: str) -> str:
        """
        提取标题部分
        
        Args:
            clean_name: 清理后的文件名
            
        Returns:
            str: 标题部分
        """
        # 查找常见的分割点
        split_keywords = ['720p', '1080p', '2160p', 'hdtv', 'web-dl', 'bluray']
        
        for keyword in split_keywords:
            pos = clean_name.lower().find(keyword)
            if pos != -1:
                return clean_name[:pos].strip()
        
        # 如果没有找到分割点，返回整个字符串
        return clean_name
    
    def _clean_title(self, title: str) -> str:
        """
        清理标题
        
        Args:
            title: 原始标题
            
        Returns:
            str: 清理后的标题
        """
        # 移除多余的空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        # 首字母大写
        words = title.split()
        cleaned_words = []
        
        for word in words:
            if len(word) > 1:
                cleaned_words.append(word.capitalize())
            elif word:
                cleaned_words.append(word.upper())
        
        return ' '.join(cleaned_words)
    
    def _format_movie_name(self, info: Dict[str, Any], pattern: str) -> str:
        """
        格式化电影名称
        
        Args:
            info: 电影信息
            pattern: 格式模式
            
        Returns:
            str: 格式化后的名称
        """
        try:
            formatted = pattern.format(
                title=info['title'],
                year=info['year'] or 'Unknown',
                resolution=info['resolution'] or ''
            )
            return self._clean_filename_for_save(formatted)
        except KeyError:
            return info['title']
    
    def _format_tv_name(self, info: Dict[str, Any], pattern: str) -> str:
        """
        格式化电视剧名称
        
        Args:
            info: 电视剧信息
            pattern: 格式模式
            
        Returns:
            str: 格式化后的名称
        """
        try:
            formatted = pattern.format(
                title=info['title'],
                season=info['season'],
                episode=info['episode'],
                year=info['year'] or '',
                resolution=info['resolution'] or ''
            )
            return self._clean_filename_for_save(formatted)
        except (KeyError, ValueError):
            return info['title']
    
    def _clean_filename_for_save(self, filename: str) -> str:
        """
        清理文件名以便保存
        
        Args:
            filename: 文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除或替换不允许的字符
        invalid_chars = r'[<>:"/\\|?*]'
        clean = re.sub(invalid_chars, '', filename)
        
        # 移除多余的空格
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
影视文件重命名工具帮助:

操作:
  rename_movies <目录> [模式]     - 重命名电影文件
  rename_tv_shows <目录> [模式]   - 重命名电视剧文件
  auto_rename <目录>             - 自动识别并重命名
  analyze <目录>                 - 分析文件信息
  organize <源目录> <目标目录>    - 组织文件到不同目录
  help                          - 显示此帮助信息

命名模式:
电影默认: {title} ({year})
电视剧默认: {title} S{season:02d}E{episode:02d}

可用变量:
  {title}      - 标题
  {year}       - 年份
  {season}     - 季数
  {episode}    - 集数
  {resolution} - 分辨率

示例:
  media_renamer auto_rename ./downloads/
  media_renamer rename_movies ./movies/ "{title} [{year}] {resolution}"
  media_renamer rename_tv_shows ./tv/ "{title} - S{season:02d}E{episode:02d}"
  media_renamer organize ./downloads/ ./organized/
  media_renamer analyze ./media/

支持的视频格式:
  .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm, .m4v, .3gp, .ts, .mts, .m2ts, .vob, .rmvb

识别功能:
- 自动识别电影和电视剧
- 提取年份、季集信息
- 识别分辨率信息
- 清理无用的标签和词汇
- 智能标题格式化
"""