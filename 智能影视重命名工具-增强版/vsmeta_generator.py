#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群晖Video Station元数据生成器
作者: OpenHands AI
版本: 2.0.1
描述: 专门为群晖Video Station生成vsmeta格式的元数据文件

vsmeta格式说明:
- 群晖Video Station专用的元数据格式
- 基于JSON结构，包含影视作品的详细信息
- 支持电影和电视剧两种类型
- 包含海报、背景图、演员、评分等信息
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import asdict

# 导入元数据类
try:
    from video_renamer_enhanced import MovieMetadata, TVMetadata
except ImportError:
    print("❌ 无法导入元数据类，请确保video_renamer_enhanced.py文件存在")


class VSMetaGenerator:
    """
    群晖Video Station元数据生成器
    
    生成符合群晖Video Station标准的vsmeta格式文件
    """
    
    def __init__(self):
        """初始化vsmeta生成器"""
        self.logger = logging.getLogger(__name__)
    
    def generate_movie_vsmeta(self, metadata: MovieMetadata, file_path: Path) -> bool:
        """
        生成电影vsmeta文件
        
        参数:
            metadata (MovieMetadata): 电影元数据
            file_path (Path): 视频文件路径
        
        返回:
            bool: 生成是否成功
        """
        try:
            vsmeta_path = file_path.with_suffix('.vsmeta')
            
            # 构建vsmeta数据结构
            vsmeta_data = {
                "version": "1",
                "type": "movie",
                "title": metadata.title or metadata.chinese_title or "Unknown",
                "original_title": metadata.original_title or "",
                "tagline": "",
                "summary": metadata.plot or "",
                "rating": self._format_rating(metadata.rating_tmdb, metadata.rating_douban),
                "year": metadata.year or 0,
                "release_date": metadata.release_date or "",
                "runtime": metadata.runtime or 0,
                "genre": metadata.genres or [],
                "director": [metadata.director] if metadata.director else [],
                "writer": [],
                "actor": self._format_actors(metadata.cast),
                "extra": {
                    "imdb": {
                        "id": metadata.imdb_id or "",
                        "rating": metadata.rating_tmdb or 0,
                        "vote": metadata.vote_count or 0
                    },
                    "tmdb": {
                        "id": metadata.tmdb_id or 0,
                        "rating": metadata.rating_tmdb or 0,
                        "vote": metadata.vote_count or 0
                    },
                    "douban": {
                        "id": metadata.douban_id or "",
                        "rating": metadata.rating_douban or 0
                    }
                },
                "poster": [
                    {
                        "url": metadata.poster_url or "",
                        "type": "poster"
                    }
                ] if metadata.poster_url else [],
                "backdrop": [
                    {
                        "url": metadata.backdrop_url or "",
                        "type": "backdrop"
                    }
                ] if metadata.backdrop_url else [],
                "certificate": "",
                "country": metadata.country or "",
                "language": metadata.language or ""
            }
            
            # 添加中文标题信息
            if metadata.chinese_title and metadata.chinese_title != metadata.title:
                vsmeta_data["title_local"] = metadata.chinese_title
            
            # 写入vsmeta文件
            with open(vsmeta_path, 'w', encoding='utf-8') as f:
                json.dump(vsmeta_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"生成电影vsmeta文件: {vsmeta_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成电影vsmeta文件失败: {e}")
            return False
    
    def generate_tv_vsmeta(self, metadata: TVMetadata, file_path: Path, season: int = 1, episode: int = 1) -> bool:
        """
        生成电视剧vsmeta文件
        
        参数:
            metadata (TVMetadata): 电视剧元数据
            file_path (Path): 视频文件路径
            season (int): 季数
            episode (int): 集数
        
        返回:
            bool: 生成是否成功
        """
        try:
            vsmeta_path = file_path.with_suffix('.vsmeta')
            
            # 构建vsmeta数据结构
            vsmeta_data = {
                "version": "1",
                "type": "tvshow",
                "title": metadata.title or metadata.chinese_title or "Unknown",
                "original_title": metadata.original_title or "",
                "tagline": "",
                "summary": metadata.plot or "",
                "rating": self._format_rating(metadata.rating_tmdb, metadata.rating_douban),
                "year": metadata.year or 0,
                "release_date": metadata.first_air_date or "",
                "runtime": metadata.episode_runtime[0] if metadata.episode_runtime else 0,
                "genre": metadata.genres or [],
                "director": [metadata.creator] if metadata.creator else [],
                "writer": [],
                "actor": self._format_actors(metadata.cast),
                "season": season,
                "episode": episode,
                "episode_count": metadata.episodes or 0,
                "season_count": metadata.seasons or 0,
                "status": metadata.status or "",
                "extra": {
                    "tmdb": {
                        "id": metadata.tmdb_id or 0,
                        "rating": metadata.rating_tmdb or 0,
                        "vote": metadata.vote_count or 0
                    },
                    "douban": {
                        "id": metadata.douban_id or "",
                        "rating": metadata.rating_douban or 0
                    }
                },
                "poster": [
                    {
                        "url": metadata.poster_url or "",
                        "type": "poster"
                    }
                ] if metadata.poster_url else [],
                "backdrop": [
                    {
                        "url": metadata.backdrop_url or "",
                        "type": "backdrop"
                    }
                ] if metadata.backdrop_url else [],
                "certificate": "",
                "country": metadata.country or "",
                "language": metadata.language or ""
            }
            
            # 添加中文标题信息
            if metadata.chinese_title and metadata.chinese_title != metadata.title:
                vsmeta_data["title_local"] = metadata.chinese_title
            
            # 写入vsmeta文件
            with open(vsmeta_path, 'w', encoding='utf-8') as f:
                json.dump(vsmeta_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"生成电视剧vsmeta文件: {vsmeta_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成电视剧vsmeta文件失败: {e}")
            return False
    
    def generate_tvshow_info_vsmeta(self, metadata: TVMetadata, show_dir: Path) -> bool:
        """
        生成电视剧信息vsmeta文件（用于剧集目录）
        
        参数:
            metadata (TVMetadata): 电视剧元数据
            show_dir (Path): 电视剧目录路径
        
        返回:
            bool: 生成是否成功
        """
        try:
            vsmeta_path = show_dir / "tvshow_info.vsmeta"
            
            # 构建电视剧信息vsmeta数据结构
            vsmeta_data = {
                "version": "1",
                "type": "tvshow_info",
                "title": metadata.title or metadata.chinese_title or "Unknown",
                "original_title": metadata.original_title or "",
                "tagline": "",
                "summary": metadata.plot or "",
                "rating": self._format_rating(metadata.rating_tmdb, metadata.rating_douban),
                "year": metadata.year or 0,
                "release_date": metadata.first_air_date or "",
                "end_date": metadata.last_air_date or "",
                "genre": metadata.genres or [],
                "director": [metadata.creator] if metadata.creator else [],
                "writer": [],
                "actor": self._format_actors(metadata.cast),
                "episode_count": metadata.episodes or 0,
                "season_count": metadata.seasons or 0,
                "status": metadata.status or "",
                "extra": {
                    "tmdb": {
                        "id": metadata.tmdb_id or 0,
                        "rating": metadata.rating_tmdb or 0,
                        "vote": metadata.vote_count or 0
                    },
                    "douban": {
                        "id": metadata.douban_id or "",
                        "rating": metadata.rating_douban or 0
                    }
                },
                "poster": [
                    {
                        "url": metadata.poster_url or "",
                        "type": "poster"
                    }
                ] if metadata.poster_url else [],
                "backdrop": [
                    {
                        "url": metadata.backdrop_url or "",
                        "type": "backdrop"
                    }
                ] if metadata.backdrop_url else [],
                "certificate": "",
                "country": metadata.country or "",
                "language": metadata.language or ""
            }
            
            # 添加中文标题信息
            if metadata.chinese_title and metadata.chinese_title != metadata.title:
                vsmeta_data["title_local"] = metadata.chinese_title
            
            # 写入vsmeta文件
            with open(vsmeta_path, 'w', encoding='utf-8') as f:
                json.dump(vsmeta_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"生成电视剧信息vsmeta文件: {vsmeta_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成电视剧信息vsmeta文件失败: {e}")
            return False
    
    def _format_rating(self, tmdb_rating: float, douban_rating: float) -> float:
        """
        格式化评分，优先使用豆瓣评分
        
        参数:
            tmdb_rating (float): TMDb评分
            douban_rating (float): 豆瓣评分
        
        返回:
            float: 格式化后的评分
        """
        if douban_rating > 0:
            return round(douban_rating, 1)
        elif tmdb_rating > 0:
            return round(tmdb_rating, 1)
        else:
            return 0.0
    
    def _format_actors(self, cast: List[str]) -> List[Dict[str, str]]:
        """
        格式化演员信息
        
        参数:
            cast (List[str]): 演员列表
        
        返回:
            List[Dict[str, str]]: 格式化后的演员信息
        """
        if not cast:
            return []
        
        actors = []
        for i, actor_name in enumerate(cast[:10]):  # 最多10个演员
            actors.append({
                "name": actor_name,
                "role": "",
                "order": i + 1
            })
        
        return actors
    
    def create_synology_directory_structure(self, base_path: Path, title: str, year: int, is_movie: bool = True) -> Path:
        """
        创建群晖Video Station标准目录结构
        
        参数:
            base_path (Path): 基础路径
            title (str): 影片标题
            year (int): 年份
            is_movie (bool): 是否为电影
        
        返回:
            Path: 创建的目录路径
        """
        try:
            if is_movie:
                # 电影目录结构: Movies/电影名 (年份)/
                movie_dir = base_path / "Movies" / f"{title} ({year})"
                movie_dir.mkdir(parents=True, exist_ok=True)
                return movie_dir
            else:
                # 电视剧目录结构: TV Shows/剧名 (年份)/Season XX/
                tv_dir = base_path / "TV Shows" / f"{title} ({year})"
                tv_dir.mkdir(parents=True, exist_ok=True)
                return tv_dir
                
        except Exception as e:
            self.logger.error(f"创建目录结构失败: {e}")
            return base_path


def create_vsmeta_example():
    """
    创建vsmeta格式示例文件
    """
    # 电影vsmeta示例
    movie_example = {
        "version": "1",
        "type": "movie",
        "title": "The Matrix",
        "title_local": "黑客帝国",
        "original_title": "The Matrix",
        "tagline": "Welcome to the Real World",
        "summary": "一名年轻的程序员被神秘的黑客墨菲斯联系，发现现实世界实际上是由机器控制的虚拟现实...",
        "rating": 8.7,
        "year": 1999,
        "release_date": "1999-03-31",
        "runtime": 136,
        "genre": ["科幻", "动作"],
        "director": ["拉娜·沃卓斯基", "莉莉·沃卓斯基"],
        "writer": ["拉娜·沃卓斯基", "莉莉·沃卓斯基"],
        "actor": [
            {"name": "基努·里维斯", "role": "尼奥", "order": 1},
            {"name": "劳伦斯·菲什伯恩", "role": "墨菲斯", "order": 2},
            {"name": "凯瑞-安·莫斯", "role": "崔妮蒂", "order": 3}
        ],
        "extra": {
            "imdb": {
                "id": "tt0133093",
                "rating": 8.7,
                "vote": 1800000
            },
            "tmdb": {
                "id": 603,
                "rating": 8.2,
                "vote": 24000
            },
            "douban": {
                "id": "1291843",
                "rating": 9.0
            }
        },
        "poster": [
            {
                "url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "type": "poster"
            }
        ],
        "backdrop": [
            {
                "url": "https://image.tmdb.org/t/p/w1280/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
                "type": "backdrop"
            }
        ],
        "certificate": "R",
        "country": "美国",
        "language": "英语"
    }
    
    # 电视剧vsmeta示例
    tv_example = {
        "version": "1",
        "type": "tvshow",
        "title": "Game of Thrones",
        "title_local": "权力的游戏",
        "original_title": "Game of Thrones",
        "tagline": "Winter is Coming",
        "summary": "在维斯特洛大陆上，几个强大的家族为了争夺铁王座而展开激烈的权力斗争...",
        "rating": 9.3,
        "year": 2011,
        "release_date": "2011-04-17",
        "runtime": 60,
        "genre": ["剧情", "奇幻", "冒险"],
        "director": ["大卫·贝尼奥夫", "D·B·威斯"],
        "writer": ["大卫·贝尼奥夫", "D·B·威斯"],
        "actor": [
            {"name": "彼特·丁拉基", "role": "提利昂·兰尼斯特", "order": 1},
            {"name": "琳娜·海蒂", "role": "瑟曦·兰尼斯特", "order": 2},
            {"name": "艾米莉亚·克拉克", "role": "丹妮莉丝·坦格利安", "order": 3}
        ],
        "season": 1,
        "episode": 1,
        "episode_count": 73,
        "season_count": 8,
        "status": "已完结",
        "extra": {
            "tmdb": {
                "id": 1399,
                "rating": 8.3,
                "vote": 22000
            },
            "douban": {
                "id": "3016187",
                "rating": 9.3
            }
        },
        "poster": [
            {
                "url": "https://image.tmdb.org/t/p/w500/7WUHnWGx5OO145IRxPDUkQSh4C7.jpg",
                "type": "poster"
            }
        ],
        "backdrop": [
            {
                "url": "https://image.tmdb.org/t/p/w1280/suopoADq0k8YZr4dQXcU6pToj6s.jpg",
                "type": "backdrop"
            }
        ],
        "certificate": "TV-MA",
        "country": "美国",
        "language": "英语"
    }
    
    # 保存示例文件
    with open("movie_example.vsmeta", 'w', encoding='utf-8') as f:
        json.dump(movie_example, f, ensure_ascii=False, indent=2)
    
    with open("tv_example.vsmeta", 'w', encoding='utf-8') as f:
        json.dump(tv_example, f, ensure_ascii=False, indent=2)
    
    print("✅ vsmeta格式示例文件已生成:")
    print("   - movie_example.vsmeta")
    print("   - tv_example.vsmeta")


if __name__ == "__main__":
    # 创建vsmeta格式示例
    create_vsmeta_example()