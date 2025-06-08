#!/usr/bin/env python3
"""
影视文件重命名工具
根据文件名自动识别电影、电视剧信息并重命名
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


class MediaRenamer:
    """影视文件重命名工具"""
    
    # 支持的视频文件扩展名
    VIDEO_EXTENSIONS = {
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', 
        '.m4v', '.3gp', '.ts', '.mts', '.m2ts', '.vob', '.rmvb'
    }
    
    # 常见的视频质量标识
    QUALITY_PATTERNS = [
        r'4K', r'2160p', r'1080p', r'720p', r'480p', r'360p',
        r'UHD', r'HD', r'SD', r'BluRay', r'BDRip', r'DVDRip',
        r'WEBRip', r'WEB-DL', r'HDTV', r'CAM', r'TS'
    ]
    
    # 常见的音频编码
    AUDIO_PATTERNS = [
        r'DTS', r'AC3', r'AAC', r'MP3', r'FLAC', r'TrueHD', r'Atmos'
    ]
    
    # 常见的视频编码
    VIDEO_CODECS = [
        r'x264', r'x265', r'H\.264', r'H\.265', r'HEVC', r'AVC'
    ]
    
    # 发布组标识
    RELEASE_GROUPS = [
        r'YIFY', r'RARBG', r'FGT', r'SPARKS', r'AMZN', r'NF', r'HULU'
    ]
    
    def __init__(self):
        self.processed_files = []
        self.errors = []
        self.operations_log = []
    
    def detect_media_type(self, filename: str) -> str:
        """检测媒体类型（电影/电视剧）"""
        filename_lower = filename.lower()
        
        # 电视剧模式检测
        tv_patterns = [
            r's\d+e\d+',  # S01E01
            r'season\s*\d+',  # Season 1
            r'\d+x\d+',  # 1x01
            r'ep\d+',  # EP01
            r'episode\s*\d+',  # Episode 1
        ]
        
        for pattern in tv_patterns:
            if re.search(pattern, filename_lower):
                return 'tv'
        
        return 'movie'
    
    def extract_movie_info(self, filename: str) -> Dict[str, str]:
        """提取电影信息"""
        info = {
            'title': '',
            'year': '',
            'quality': '',
            'source': '',
            'codec': '',
            'audio': '',
            'group': '',
            'extension': ''
        }
        
        # 获取扩展名
        path = Path(filename)
        info['extension'] = path.suffix
        name_without_ext = path.stem
        
        # 提取年份
        year_match = re.search(r'\b(19|20)\d{2}\b', name_without_ext)
        if year_match:
            info['year'] = year_match.group()
            # 移除年份后的部分通常是标题
            title_part = name_without_ext[:year_match.start()].strip()
            info['title'] = re.sub(r'[._-]+', ' ', title_part).strip()
        else:
            # 没有年份，尝试其他方法提取标题
            info['title'] = re.sub(r'[._-]+', ' ', name_without_ext).strip()
        
        # 提取质量信息
        for quality in self.QUALITY_PATTERNS:
            if re.search(quality, name_without_ext, re.IGNORECASE):
                info['quality'] = quality
                break
        
        # 提取音频信息
        for audio in self.AUDIO_PATTERNS:
            if re.search(audio, name_without_ext, re.IGNORECASE):
                info['audio'] = audio
                break
        
        # 提取视频编码
        for codec in self.VIDEO_CODECS:
            if re.search(codec, name_without_ext, re.IGNORECASE):
                info['codec'] = codec
                break
        
        # 提取发布组
        for group in self.RELEASE_GROUPS:
            if re.search(group, name_without_ext, re.IGNORECASE):
                info['group'] = group
                break
        
        return info
    
    def extract_tv_info(self, filename: str) -> Dict[str, str]:
        """提取电视剧信息"""
        info = {
            'title': '',
            'season': '',
            'episode': '',
            'episode_title': '',
            'quality': '',
            'source': '',
            'codec': '',
            'audio': '',
            'group': '',
            'extension': ''
        }
        
        # 获取扩展名
        path = Path(filename)
        info['extension'] = path.suffix
        name_without_ext = path.stem
        
        # 提取季集信息
        # S01E01 格式
        se_match = re.search(r'[Ss](\d+)[Ee](\d+)', name_without_ext)
        if se_match:
            info['season'] = se_match.group(1).zfill(2)
            info['episode'] = se_match.group(2).zfill(2)
            title_part = name_without_ext[:se_match.start()].strip()
            info['title'] = re.sub(r'[._-]+', ' ', title_part).strip()
        else:
            # 1x01 格式
            x_match = re.search(r'(\d+)x(\d+)', name_without_ext)
            if x_match:
                info['season'] = x_match.group(1).zfill(2)
                info['episode'] = x_match.group(2).zfill(2)
                title_part = name_without_ext[:x_match.start()].strip()
                info['title'] = re.sub(r'[._-]+', ' ', title_part).strip()
        
        # 提取其他信息（与电影相同）
        for quality in self.QUALITY_PATTERNS:
            if re.search(quality, name_without_ext, re.IGNORECASE):
                info['quality'] = quality
                break
        
        for audio in self.AUDIO_PATTERNS:
            if re.search(audio, name_without_ext, re.IGNORECASE):
                info['audio'] = audio
                break
        
        for codec in self.VIDEO_CODECS:
            if re.search(codec, name_without_ext, re.IGNORECASE):
                info['codec'] = codec
                break
        
        for group in self.RELEASE_GROUPS:
            if re.search(group, name_without_ext, re.IGNORECASE):
                info['group'] = group
                break
        
        return info
    
    def generate_movie_name(self, info: Dict[str, str], template: str = None) -> str:
        """生成电影文件名"""
        if template is None:
            template = "{title} ({year}) [{quality}]{extension}"
        
        # 清理标题
        title = info['title'].title() if info['title'] else 'Unknown Movie'
        
        # 构建文件名
        name_parts = []
        if info['title']:
            name_parts.append(title)
        if info['year']:
            name_parts.append(f"({info['year']})")
        
        # 添加质量信息
        quality_parts = []
        if info['quality']:
            quality_parts.append(info['quality'])
        if info['codec']:
            quality_parts.append(info['codec'])
        if info['audio']:
            quality_parts.append(info['audio'])
        
        if quality_parts:
            name_parts.append(f"[{'.'.join(quality_parts)}]")
        
        if info['group']:
            name_parts.append(f"-{info['group']}")
        
        filename = ' '.join(name_parts) + info['extension']
        
        # 清理文件名中的非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename
    
    def generate_tv_name(self, info: Dict[str, str], template: str = None) -> str:
        """生成电视剧文件名"""
        if template is None:
            template = "{title} S{season}E{episode} [{quality}]{extension}"
        
        # 清理标题
        title = info['title'].title() if info['title'] else 'Unknown TV Show'
        
        # 构建文件名
        name_parts = []
        if info['title']:
            name_parts.append(title)
        
        if info['season'] and info['episode']:
            name_parts.append(f"S{info['season']}E{info['episode']}")
        
        if info['episode_title']:
            name_parts.append(f"- {info['episode_title']}")
        
        # 添加质量信息
        quality_parts = []
        if info['quality']:
            quality_parts.append(info['quality'])
        if info['codec']:
            quality_parts.append(info['codec'])
        if info['audio']:
            quality_parts.append(info['audio'])
        
        if quality_parts:
            name_parts.append(f"[{'.'.join(quality_parts)}]")
        
        if info['group']:
            name_parts.append(f"-{info['group']}")
        
        filename = ' '.join(name_parts) + info['extension']
        
        # 清理文件名中的非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        
        return filename
    
    def rename_media_files(self, directory: str, preview: bool = True, 
                          movie_template: str = None, tv_template: str = None) -> Dict:
        """批量重命名媒体文件"""
        directory_path = Path(directory)
        if not directory_path.exists():
            error_msg = f"目录不存在: {directory}"
            self.errors.append(error_msg)
            return {'renamed': [], 'errors': [error_msg]}
        
        renamed_files = []
        errors = []
        
        # 获取所有视频文件
        video_files = []
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.VIDEO_EXTENSIONS:
                video_files.append(file_path)
        
        if not video_files:
            error_msg = f"在目录 {directory} 中未找到视频文件"
            self.errors.append(error_msg)
            return {'renamed': [], 'errors': [error_msg]}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🎬 处理媒体文件", total=len(video_files))
            
            for file_path in video_files:
                try:
                    progress.update(task, description=f"处理: {file_path.name}")
                    
                    # 检测媒体类型
                    media_type = self.detect_media_type(file_path.name)
                    
                    # 提取信息
                    if media_type == 'movie':
                        info = self.extract_movie_info(file_path.name)
                        new_name = self.generate_movie_name(info, movie_template)
                    else:
                        info = self.extract_tv_info(file_path.name)
                        new_name = self.generate_tv_name(info, tv_template)
                    
                    new_path = file_path.parent / new_name
                    
                    # 检查是否需要重命名
                    if file_path.name == new_name:
                        self.operations_log.append(f"跳过: {file_path.name} (无需重命名)")
                        progress.advance(task)
                        continue
                    
                    # 检查目标文件是否已存在
                    if new_path.exists() and new_path != file_path:
                        error_msg = f"目标文件已存在: {new_name}"
                        errors.append(error_msg)
                        self.errors.append(error_msg)
                        progress.advance(task)
                        continue
                    
                    rename_info = {
                        'original': str(file_path),
                        'new': str(new_path),
                        'original_name': file_path.name,
                        'new_name': new_name,
                        'media_type': media_type,
                        'info': info
                    }
                    
                    if not preview:
                        # 执行重命名
                        file_path.rename(new_path)
                        self.processed_files.append(rename_info)
                        self.operations_log.append(f"重命名: {file_path.name} -> {new_name}")
                    else:
                        self.operations_log.append(f"预览: {file_path.name} -> {new_name}")
                    
                    renamed_files.append(rename_info)
                    
                except Exception as e:
                    error_msg = f"处理文件 {file_path.name} 时出错: {str(e)}"
                    errors.append(error_msg)
                    self.errors.append(error_msg)
                
                progress.advance(task)
        
        return {
            'renamed': renamed_files,
            'errors': errors,
            'total_processed': len(renamed_files),
            'total_errors': len(errors)
        }
    
    def organize_by_type(self, directory: str, preview: bool = True) -> Dict:
        """按类型组织媒体文件（电影/电视剧）"""
        directory_path = Path(directory)
        if not directory_path.exists():
            error_msg = f"目录不存在: {directory}"
            self.errors.append(error_msg)
            return {'organized': [], 'errors': [error_msg]}
        
        organized_files = []
        errors = []
        
        # 创建目标目录
        movies_dir = directory_path / "Movies"
        tv_shows_dir = directory_path / "TV Shows"
        
        if not preview:
            movies_dir.mkdir(exist_ok=True)
            tv_shows_dir.mkdir(exist_ok=True)
        
        # 获取所有视频文件
        video_files = []
        for file_path in directory_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.VIDEO_EXTENSIONS:
                video_files.append(file_path)
        
        for file_path in video_files:
            try:
                media_type = self.detect_media_type(file_path.name)
                target_dir = movies_dir if media_type == 'movie' else tv_shows_dir
                new_path = target_dir / file_path.name
                
                organize_info = {
                    'original': str(file_path),
                    'new': str(new_path),
                    'media_type': media_type
                }
                
                if not preview:
                    file_path.rename(new_path)
                    self.processed_files.append(organize_info)
                    self.operations_log.append(f"移动: {file_path.name} -> {media_type}")
                else:
                    self.operations_log.append(f"预览移动: {file_path.name} -> {media_type}")
                
                organized_files.append(organize_info)
                
            except Exception as e:
                error_msg = f"组织文件 {file_path.name} 时出错: {str(e)}"
                errors.append(error_msg)
                self.errors.append(error_msg)
        
        return {
            'organized': organized_files,
            'errors': errors,
            'total_organized': len(organized_files),
            'total_errors': len(errors)
        }
    
    def get_report(self) -> Dict:
        """获取处理报告"""
        return {
            'processed_files': self.processed_files,
            'errors': self.errors,
            'operations_log': self.operations_log,
            'total_processed': len(self.processed_files),
            'total_errors': len(self.errors)
        }
    
    def display_preview(self, result: Dict):
        """显示预览结果"""
        if 'renamed' in result:
            console.print("\n👀 预览结果:")
            for item in result['renamed']:
                console.print(f"  • {item['original_name']} -> {item['new_name']}")
        
        if 'organized' in result:
            console.print("\n📁 组织预览:")
            for item in result['organized']:
                console.print(f"  • {Path(item['original']).name} -> {item['media_type']}")
    
    def display_report(self):
        """显示处理报告"""
        report = self.get_report()
        
        # 创建统计表格
        table = Table(title="📊 媒体文件处理报告")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="magenta")
        
        table.add_row("处理成功", str(report['total_processed']))
        table.add_row("处理失败", str(report['total_errors']))
        table.add_row("总操作数", str(len(report['operations_log'])))
        
        console.print(table)
        
        # 显示操作日志
        if report['operations_log']:
            console.print("\n📝 操作日志:")
            for log in report['operations_log'][-10:]:  # 显示最后10条
                console.print(f"  • {log}")
            
            if len(report['operations_log']) > 10:
                console.print(f"  ... 还有 {len(report['operations_log']) - 10} 条记录")
        
        # 显示错误
        if report['errors']:
            console.print("\n❌ 错误信息:")
            for error in report['errors']:
                console.print(f"  • {error}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="影视文件重命名工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 重命名命令
    rename_parser = subparsers.add_parser('rename', help='重命名媒体文件')
    rename_parser.add_argument('directory', help='目标目录')
    rename_parser.add_argument('--preview', action='store_true', help='预览模式')
    rename_parser.add_argument('--movie-template', help='电影文件名模板')
    rename_parser.add_argument('--tv-template', help='电视剧文件名模板')
    
    # 组织命令
    organize_parser = subparsers.add_parser('organize', help='按类型组织文件')
    organize_parser.add_argument('directory', help='目标目录')
    organize_parser.add_argument('--preview', action='store_true', help='预览模式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    renamer = MediaRenamer()
    
    try:
        if args.command == 'rename':
            console.print(f"🎬 重命名媒体文件: {args.directory}")
            result = renamer.rename_media_files(
                args.directory,
                preview=args.preview,
                movie_template=args.movie_template,
                tv_template=args.tv_template
            )
            
            if args.preview:
                renamer.display_preview(result)
            
        elif args.command == 'organize':
            console.print(f"📁 组织媒体文件: {args.directory}")
            result = renamer.organize_by_type(args.directory, preview=args.preview)
            
            if args.preview:
                renamer.display_preview(result)
        
        # 显示报告
        renamer.display_report()
        
    except KeyboardInterrupt:
        console.print("\n⚠️ 操作被用户取消")
    except Exception as e:
        console.print(f"\n❌ 执行失败: {str(e)}")


if __name__ == "__main__":
    main()