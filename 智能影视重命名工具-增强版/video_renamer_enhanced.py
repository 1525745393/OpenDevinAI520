#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能影视文件重命名工具 - 增强版
作者: OpenHands AI
版本: 2.0.0
描述: 集成TMDb和豆瓣API的智能影视文件重命名工具

新增功能:
1. TMDb API集成 - 获取国际影视数据
2. 豆瓣API集成 - 获取中文影视数据
3. 智能匹配算法 - 自动选择最佳匹配结果
4. 元数据缓存 - 避免重复API调用
5. 海报下载 - 自动下载影片海报
6. NFO文件生成 - 生成媒体中心元数据文件
7. 多语言支持 - 中英文标题处理
8. 评分信息 - 获取影片评分和简介
"""

import os
import sys
import re
import json
import logging
import platform
import datetime
import time
import hashlib
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
import threading
import queue

# 导入基础重命名工具
from video_renamer import VideoRenamer, VideoInfo


@dataclass
class MovieMetadata:
    """
    电影元数据类
    
    存储从API获取的详细电影信息
    """
    tmdb_id: Optional[int] = None
    douban_id: Optional[str] = None
    title: str = ""
    original_title: str = ""
    chinese_title: str = ""
    year: int = 0
    release_date: str = ""
    runtime: int = 0
    genres: List[str] = None
    director: str = ""
    cast: List[str] = None
    plot: str = ""
    rating_tmdb: float = 0.0
    rating_douban: float = 0.0
    vote_count: int = 0
    poster_url: str = ""
    backdrop_url: str = ""
    language: str = ""
    country: str = ""
    imdb_id: str = ""
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []
        if self.cast is None:
            self.cast = []


@dataclass
class TVMetadata:
    """
    电视剧元数据类
    
    存储从API获取的详细电视剧信息
    """
    tmdb_id: Optional[int] = None
    douban_id: Optional[str] = None
    title: str = ""
    original_title: str = ""
    chinese_title: str = ""
    year: int = 0
    first_air_date: str = ""
    last_air_date: str = ""
    episode_runtime: List[int] = None
    genres: List[str] = None
    creator: str = ""
    cast: List[str] = None
    plot: str = ""
    rating_tmdb: float = 0.0
    rating_douban: float = 0.0
    vote_count: int = 0
    poster_url: str = ""
    backdrop_url: str = ""
    language: str = ""
    country: str = ""
    seasons: int = 0
    episodes: int = 0
    status: str = ""
    
    def __post_init__(self):
        if self.episode_runtime is None:
            self.episode_runtime = []
        if self.genres is None:
            self.genres = []
        if self.cast is None:
            self.cast = []


class APIClient:
    """
    API客户端基类
    
    提供通用的API调用功能
    """
    
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        """
        初始化API客户端
        
        参数:
            base_url (str): API基础URL
            headers (Dict[str, str]): 请求头
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.session_cache = {}
        self.rate_limit_delay = 0.5  # API调用间隔（秒）
        self.last_request_time = 0
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        发起API请求
        
        参数:
            endpoint (str): API端点
            params (Dict[str, Any]): 请求参数
        
        返回:
            Optional[Dict[str, Any]]: API响应数据
        """
        try:
            # 速率限制
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - time_since_last)
            
            # 构建URL
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            # 创建请求
            request = urllib.request.Request(url, headers=self.headers)
            
            # 发起请求
            with urllib.request.urlopen(request, timeout=10) as response:
                data = response.read().decode('utf-8')
                self.last_request_time = time.time()
                return json.loads(data)
                
        except urllib.error.HTTPError as e:
            if e.code == 429:  # 速率限制
                time.sleep(2)
                return self._make_request(endpoint, params)
            logging.warning(f"HTTP错误 {e.code}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            logging.warning(f"URL错误: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            logging.warning(f"JSON解析错误: {e}")
            return None
        except Exception as e:
            logging.error(f"API请求失败: {e}")
            return None


class TMDbClient(APIClient):
    """
    TMDb API客户端
    
    用于获取国际影视数据
    """
    
    def __init__(self, api_key: str):
        """
        初始化TMDb客户端
        
        参数:
            api_key (str): TMDb API密钥
        """
        super().__init__(
            base_url="https://api.themoviedb.org/3",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        self.api_key = api_key
        self.image_base_url = "https://image.tmdb.org/t/p/"
    
    def search_movie(self, title: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        搜索电影
        
        参数:
            title (str): 电影标题
            year (Optional[int]): 年份
        
        返回:
            List[Dict[str, Any]]: 搜索结果列表
        """
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "zh-CN"
        }
        
        if year:
            params["year"] = year
        
        response = self._make_request("search/movie", params)
        return response.get("results", []) if response else []
    
    def search_tv(self, title: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        搜索电视剧
        
        参数:
            title (str): 电视剧标题
            year (Optional[int]): 年份
        
        返回:
            List[Dict[str, Any]]: 搜索结果列表
        """
        params = {
            "api_key": self.api_key,
            "query": title,
            "language": "zh-CN"
        }
        
        if year:
            params["first_air_date_year"] = year
        
        response = self._make_request("search/tv", params)
        return response.get("results", []) if response else []
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        获取电影详细信息
        
        参数:
            movie_id (int): 电影ID
        
        返回:
            Optional[Dict[str, Any]]: 电影详细信息
        """
        params = {
            "api_key": self.api_key,
            "language": "zh-CN",
            "append_to_response": "credits,external_ids"
        }
        
        return self._make_request(f"movie/{movie_id}", params)
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict[str, Any]]:
        """
        获取电视剧详细信息
        
        参数:
            tv_id (int): 电视剧ID
        
        返回:
            Optional[Dict[str, Any]]: 电视剧详细信息
        """
        params = {
            "api_key": self.api_key,
            "language": "zh-CN",
            "append_to_response": "credits,external_ids"
        }
        
        return self._make_request(f"tv/{tv_id}", params)
    
    def get_image_url(self, path: str, size: str = "w500") -> str:
        """
        获取图片完整URL
        
        参数:
            path (str): 图片路径
            size (str): 图片尺寸
        
        返回:
            str: 完整图片URL
        """
        if not path:
            return ""
        return f"{self.image_base_url}{size}{path}"


class DoubanClient(APIClient):
    """
    豆瓣API客户端
    
    用于获取中文影视数据
    """
    
    def __init__(self):
        """初始化豆瓣客户端"""
        super().__init__(
            base_url="https://frodo.douban.com/api/v2",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://movie.douban.com/"
            }
        )
        self.rate_limit_delay = 1.0  # 豆瓣需要更长的间隔
    
    def search_movie(self, title: str) -> List[Dict[str, Any]]:
        """
        搜索电影
        
        参数:
            title (str): 电影标题
        
        返回:
            List[Dict[str, Any]]: 搜索结果列表
        """
        params = {
            "q": title,
            "count": 10
        }
        
        response = self._make_request("search/movie", params)
        return response.get("subjects", []) if response else []
    
    def search_tv(self, title: str) -> List[Dict[str, Any]]:
        """
        搜索电视剧
        
        参数:
            title (str): 电视剧标题
        
        返回:
            List[Dict[str, Any]]: 搜索结果列表
        """
        params = {
            "q": title,
            "count": 10
        }
        
        response = self._make_request("search/tv", params)
        return response.get("subjects", []) if response else []
    
    def get_movie_details(self, movie_id: str) -> Optional[Dict[str, Any]]:
        """
        获取电影详细信息
        
        参数:
            movie_id (str): 电影ID
        
        返回:
            Optional[Dict[str, Any]]: 电影详细信息
        """
        return self._make_request(f"movie/{movie_id}")
    
    def get_tv_details(self, tv_id: str) -> Optional[Dict[str, Any]]:
        """
        获取电视剧详细信息
        
        参数:
            tv_id (str): 电视剧ID
        
        返回:
            Optional[Dict[str, Any]]: 电视剧详细信息
        """
        return self._make_request(f"tv/{tv_id}")


class MetadataCache:
    """
    元数据缓存管理器
    
    用于缓存API查询结果，避免重复请求
    """
    
    def __init__(self, cache_dir: Path):
        """
        初始化缓存管理器
        
        参数:
            cache_dir (Path): 缓存目录
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "metadata_cache.json"
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """
        加载缓存数据
        
        返回:
            Dict[str, Any]: 缓存数据
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.warning(f"加载缓存失败: {e}")
        
        return {}
    
    def _save_cache(self) -> None:
        """保存缓存数据"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存缓存失败: {e}")
    
    def _get_cache_key(self, title: str, year: Optional[int] = None, media_type: str = "movie") -> str:
        """
        生成缓存键
        
        参数:
            title (str): 标题
            year (Optional[int]): 年份
            media_type (str): 媒体类型
        
        返回:
            str: 缓存键
        """
        key_data = f"{media_type}:{title}:{year or 'unknown'}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get(self, title: str, year: Optional[int] = None, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """
        获取缓存数据
        
        参数:
            title (str): 标题
            year (Optional[int]): 年份
            media_type (str): 媒体类型
        
        返回:
            Optional[Dict[str, Any]]: 缓存的元数据
        """
        cache_key = self._get_cache_key(title, year, media_type)
        cached_data = self.cache_data.get(cache_key)
        
        if cached_data:
            # 检查缓存是否过期（7天）
            cache_time = cached_data.get("cache_time", 0)
            if time.time() - cache_time < 7 * 24 * 3600:
                return cached_data.get("data")
        
        return None
    
    def set(self, title: str, data: Dict[str, Any], year: Optional[int] = None, media_type: str = "movie") -> None:
        """
        设置缓存数据
        
        参数:
            title (str): 标题
            data (Dict[str, Any]): 元数据
            year (Optional[int]): 年份
            media_type (str): 媒体类型
        """
        cache_key = self._get_cache_key(title, year, media_type)
        self.cache_data[cache_key] = {
            "data": data,
            "cache_time": time.time()
        }
        self._save_cache()


class MetadataFetcher:
    """
    元数据获取器
    
    整合TMDb和豆瓣API，智能获取最佳元数据
    """
    
    def __init__(self, config: Dict[str, Any], cache_dir: Path):
        """
        初始化元数据获取器
        
        参数:
            config (Dict[str, Any]): 配置信息
            cache_dir (Path): 缓存目录
        """
        self.config = config
        self.cache = MetadataCache(cache_dir)
        
        # 初始化API客户端
        tmdb_config = config.get("api_settings", {}).get("tmdb", {})
        if tmdb_config.get("enabled", False) and tmdb_config.get("api_key"):
            self.tmdb_client = TMDbClient(tmdb_config["api_key"])
        else:
            self.tmdb_client = None
        
        douban_config = config.get("api_settings", {}).get("douban", {})
        if douban_config.get("enabled", False):
            self.douban_client = DoubanClient()
        else:
            self.douban_client = None
        
        self.logger = logging.getLogger(__name__)
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算字符串相似度
        
        参数:
            str1 (str): 字符串1
            str2 (str): 字符串2
        
        返回:
            float: 相似度分数 (0-1)
        """
        if not str1 or not str2:
            return 0.0
        
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        if str1 == str2:
            return 1.0
        
        # 简单的编辑距离算法
        len1, len2 = len(str1), len(str2)
        if len1 > len2:
            str1, str2 = str2, str1
            len1, len2 = len2, len1
        
        current_row = range(len1 + 1)
        for i in range(1, len2 + 1):
            previous_row, current_row = current_row, [i] + [0] * len1
            for j in range(1, len1 + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if str1[j - 1] != str2[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)
        
        return 1.0 - (current_row[len1] / max(len1, len2))
    
    def _find_best_match(self, search_results: List[Dict[str, Any]], target_title: str, target_year: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        从搜索结果中找到最佳匹配
        
        参数:
            search_results (List[Dict[str, Any]]): 搜索结果
            target_title (str): 目标标题
            target_year (Optional[int]): 目标年份
        
        返回:
            Optional[Dict[str, Any]]: 最佳匹配结果
        """
        if not search_results:
            return None
        
        best_match = None
        best_score = 0.0
        
        for result in search_results:
            score = 0.0
            
            # 标题匹配分数
            title = result.get("title", "") or result.get("name", "")
            original_title = result.get("original_title", "") or result.get("original_name", "")
            
            title_score = max(
                self._calculate_similarity(target_title, title),
                self._calculate_similarity(target_title, original_title)
            )
            score += title_score * 0.7
            
            # 年份匹配分数
            if target_year:
                release_date = result.get("release_date", "") or result.get("first_air_date", "")
                if release_date:
                    try:
                        result_year = int(release_date.split("-")[0])
                        year_diff = abs(target_year - result_year)
                        if year_diff == 0:
                            score += 0.3
                        elif year_diff <= 1:
                            score += 0.2
                        elif year_diff <= 2:
                            score += 0.1
                    except (ValueError, IndexError):
                        pass
            
            # 流行度分数
            popularity = result.get("popularity", 0)
            if popularity > 0:
                score += min(popularity / 1000, 0.1)
            
            if score > best_score:
                best_score = score
                best_match = result
        
        # 只有当匹配分数足够高时才返回结果
        if best_score >= 0.6:
            return best_match
        
        return None
    
    def fetch_movie_metadata(self, title: str, year: Optional[int] = None) -> Optional[MovieMetadata]:
        """
        获取电影元数据
        
        参数:
            title (str): 电影标题
            year (Optional[int]): 年份
        
        返回:
            Optional[MovieMetadata]: 电影元数据
        """
        # 检查缓存
        cached_data = self.cache.get(title, year, "movie")
        if cached_data:
            self.logger.info(f"从缓存获取电影元数据: {title}")
            return MovieMetadata(**cached_data)
        
        metadata = MovieMetadata()
        metadata.title = title
        metadata.year = year or 0
        
        # 尝试从TMDb获取数据
        if self.tmdb_client:
            try:
                self.logger.info(f"从TMDb搜索电影: {title}")
                search_results = self.tmdb_client.search_movie(title, year)
                best_match = self._find_best_match(search_results, title, year)
                
                if best_match:
                    movie_id = best_match["id"]
                    details = self.tmdb_client.get_movie_details(movie_id)
                    
                    if details:
                        metadata.tmdb_id = movie_id
                        metadata.title = details.get("title", title)
                        metadata.original_title = details.get("original_title", "")
                        metadata.year = int(details.get("release_date", "").split("-")[0]) if details.get("release_date") else year or 0
                        metadata.release_date = details.get("release_date", "")
                        metadata.runtime = details.get("runtime", 0)
                        metadata.genres = [g["name"] for g in details.get("genres", [])]
                        metadata.plot = details.get("overview", "")
                        metadata.rating_tmdb = details.get("vote_average", 0.0)
                        metadata.vote_count = details.get("vote_count", 0)
                        metadata.poster_url = self.tmdb_client.get_image_url(details.get("poster_path", ""))
                        metadata.backdrop_url = self.tmdb_client.get_image_url(details.get("backdrop_path", ""))
                        metadata.language = details.get("original_language", "")
                        
                        # 获取导演和演员信息
                        credits = details.get("credits", {})
                        crew = credits.get("crew", [])
                        cast = credits.get("cast", [])
                        
                        for person in crew:
                            if person.get("job") == "Director":
                                metadata.director = person.get("name", "")
                                break
                        
                        metadata.cast = [person.get("name", "") for person in cast[:5]]
                        
                        # 获取IMDB ID
                        external_ids = details.get("external_ids", {})
                        metadata.imdb_id = external_ids.get("imdb_id", "")
                        
                        self.logger.info(f"TMDb获取成功: {metadata.title} ({metadata.year})")
                
            except Exception as e:
                self.logger.error(f"TMDb API错误: {e}")
        
        # 尝试从豆瓣获取中文数据
        if self.douban_client:
            try:
                self.logger.info(f"从豆瓣搜索电影: {title}")
                search_results = self.douban_client.search_movie(title)
                best_match = self._find_best_match(search_results, title, year)
                
                if best_match:
                    movie_id = best_match["id"]
                    details = self.douban_client.get_movie_details(movie_id)
                    
                    if details:
                        metadata.douban_id = movie_id
                        metadata.chinese_title = details.get("title", "")
                        metadata.rating_douban = details.get("rating", {}).get("average", 0.0)
                        
                        # 如果TMDb没有获取到中文信息，使用豆瓣的
                        if not metadata.title or not self._is_chinese(metadata.title):
                            metadata.title = metadata.chinese_title
                        
                        self.logger.info(f"豆瓣获取成功: {metadata.chinese_title}")
                
            except Exception as e:
                self.logger.error(f"豆瓣API错误: {e}")
        
        # 缓存结果
        if metadata.tmdb_id or metadata.douban_id:
            self.cache.set(title, asdict(metadata), year, "movie")
            return metadata
        
        return None
    
    def fetch_tv_metadata(self, title: str, year: Optional[int] = None) -> Optional[TVMetadata]:
        """
        获取电视剧元数据
        
        参数:
            title (str): 电视剧标题
            year (Optional[int]): 年份
        
        返回:
            Optional[TVMetadata]: 电视剧元数据
        """
        # 检查缓存
        cached_data = self.cache.get(title, year, "tv")
        if cached_data:
            self.logger.info(f"从缓存获取电视剧元数据: {title}")
            return TVMetadata(**cached_data)
        
        metadata = TVMetadata()
        metadata.title = title
        metadata.year = year or 0
        
        # 尝试从TMDb获取数据
        if self.tmdb_client:
            try:
                self.logger.info(f"从TMDb搜索电视剧: {title}")
                search_results = self.tmdb_client.search_tv(title, year)
                best_match = self._find_best_match(search_results, title, year)
                
                if best_match:
                    tv_id = best_match["id"]
                    details = self.tmdb_client.get_tv_details(tv_id)
                    
                    if details:
                        metadata.tmdb_id = tv_id
                        metadata.title = details.get("name", title)
                        metadata.original_title = details.get("original_name", "")
                        metadata.year = int(details.get("first_air_date", "").split("-")[0]) if details.get("first_air_date") else year or 0
                        metadata.first_air_date = details.get("first_air_date", "")
                        metadata.last_air_date = details.get("last_air_date", "")
                        metadata.episode_runtime = details.get("episode_run_time", [])
                        metadata.genres = [g["name"] for g in details.get("genres", [])]
                        metadata.plot = details.get("overview", "")
                        metadata.rating_tmdb = details.get("vote_average", 0.0)
                        metadata.vote_count = details.get("vote_count", 0)
                        metadata.poster_url = self.tmdb_client.get_image_url(details.get("poster_path", ""))
                        metadata.backdrop_url = self.tmdb_client.get_image_url(details.get("backdrop_path", ""))
                        metadata.language = details.get("original_language", "")
                        metadata.seasons = details.get("number_of_seasons", 0)
                        metadata.episodes = details.get("number_of_episodes", 0)
                        metadata.status = details.get("status", "")
                        
                        # 获取创作者和演员信息
                        creators = details.get("created_by", [])
                        if creators:
                            metadata.creator = creators[0].get("name", "")
                        
                        credits = details.get("credits", {})
                        cast = credits.get("cast", [])
                        metadata.cast = [person.get("name", "") for person in cast[:5]]
                        
                        self.logger.info(f"TMDb获取成功: {metadata.title} ({metadata.year})")
                
            except Exception as e:
                self.logger.error(f"TMDb API错误: {e}")
        
        # 尝试从豆瓣获取中文数据
        if self.douban_client:
            try:
                self.logger.info(f"从豆瓣搜索电视剧: {title}")
                search_results = self.douban_client.search_tv(title)
                best_match = self._find_best_match(search_results, title, year)
                
                if best_match:
                    tv_id = best_match["id"]
                    details = self.douban_client.get_tv_details(tv_id)
                    
                    if details:
                        metadata.douban_id = tv_id
                        metadata.chinese_title = details.get("title", "")
                        metadata.rating_douban = details.get("rating", {}).get("average", 0.0)
                        
                        # 如果TMDb没有获取到中文信息，使用豆瓣的
                        if not metadata.title or not self._is_chinese(metadata.title):
                            metadata.title = metadata.chinese_title
                        
                        self.logger.info(f"豆瓣获取成功: {metadata.chinese_title}")
                
            except Exception as e:
                self.logger.error(f"豆瓣API错误: {e}")
        
        # 缓存结果
        if metadata.tmdb_id or metadata.douban_id:
            self.cache.set(title, asdict(metadata), year, "tv")
            return metadata
        
        return None
    
    def _is_chinese(self, text: str) -> bool:
        """
        检查文本是否包含中文字符
        
        参数:
            text (str): 要检查的文本
        
        返回:
            bool: 是否包含中文
        """
        if not text:
            return False
        
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return True
        
        return False


class NFOGenerator:
    """
    NFO文件生成器
    
    为媒体中心生成元数据文件
    支持标准NFO格式和群晖vsmeta格式
    """
    
    def __init__(self):
        """初始化NFO生成器"""
        self.logger = logging.getLogger(__name__)
        
        # 导入vsmeta生成器
        try:
            from vsmeta_generator import VSMetaGenerator
            self.vsmeta_generator = VSMetaGenerator()
        except ImportError:
            self.vsmeta_generator = None
            self.logger.warning("vsmeta生成器导入失败，将只支持标准NFO格式")
    
    def generate_movie_nfo(self, metadata: MovieMetadata, file_path: Path, format_type: str = "nfo") -> bool:
        """
        生成电影元数据文件
        
        参数:
            metadata (MovieMetadata): 电影元数据
            file_path (Path): 视频文件路径
            format_type (str): 格式类型 ("nfo" 或 "vsmeta")
        
        返回:
            bool: 生成是否成功
        """
        if format_type == "vsmeta" and self.vsmeta_generator:
            return self.vsmeta_generator.generate_movie_vsmeta(metadata, file_path)
        else:
            return self._generate_movie_nfo_xml(metadata, file_path)
    
    def _generate_movie_nfo_xml(self, metadata: MovieMetadata, file_path: Path) -> bool:
        """
        生成标准NFO格式的电影文件
        
        参数:
            metadata (MovieMetadata): 电影元数据
            file_path (Path): 视频文件路径
        
        返回:
            bool: 生成是否成功
        """
        try:
            nfo_path = file_path.with_suffix('.nfo')
            
            # 创建XML结构
            movie = ET.Element("movie")
            
            # 基本信息
            ET.SubElement(movie, "title").text = metadata.title
            if metadata.original_title:
                ET.SubElement(movie, "originaltitle").text = metadata.original_title
            if metadata.year:
                ET.SubElement(movie, "year").text = str(metadata.year)
            if metadata.release_date:
                ET.SubElement(movie, "premiered").text = metadata.release_date
            if metadata.runtime:
                ET.SubElement(movie, "runtime").text = str(metadata.runtime)
            if metadata.plot:
                ET.SubElement(movie, "plot").text = metadata.plot
            if metadata.director:
                ET.SubElement(movie, "director").text = metadata.director
            
            # 评分信息
            if metadata.rating_tmdb > 0:
                rating = ET.SubElement(movie, "rating")
                rating.set("name", "tmdb")
                rating.set("max", "10")
                ET.SubElement(rating, "value").text = str(metadata.rating_tmdb)
                if metadata.vote_count:
                    ET.SubElement(rating, "votes").text = str(metadata.vote_count)
            
            if metadata.rating_douban > 0:
                rating = ET.SubElement(movie, "rating")
                rating.set("name", "douban")
                rating.set("max", "10")
                ET.SubElement(rating, "value").text = str(metadata.rating_douban)
            
            # 类型
            for genre in metadata.genres:
                ET.SubElement(movie, "genre").text = genre
            
            # 演员
            for actor_name in metadata.cast:
                actor = ET.SubElement(movie, "actor")
                ET.SubElement(actor, "name").text = actor_name
            
            # ID信息
            if metadata.tmdb_id:
                uniqueid = ET.SubElement(movie, "uniqueid")
                uniqueid.set("type", "tmdb")
                uniqueid.text = str(metadata.tmdb_id)
            
            if metadata.imdb_id:
                uniqueid = ET.SubElement(movie, "uniqueid")
                uniqueid.set("type", "imdb")
                uniqueid.text = metadata.imdb_id
            
            if metadata.douban_id:
                uniqueid = ET.SubElement(movie, "uniqueid")
                uniqueid.set("type", "douban")
                uniqueid.text = metadata.douban_id
            
            # 写入文件
            tree = ET.ElementTree(movie)
            ET.indent(tree, space="  ", level=0)
            tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"生成电影NFO文件: {nfo_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成电影NFO文件失败: {e}")
            return False
    
    def generate_tv_nfo(self, metadata: TVMetadata, file_path: Path, format_type: str = "nfo", season: int = 1, episode: int = 1) -> bool:
        """
        生成电视剧元数据文件
        
        参数:
            metadata (TVMetadata): 电视剧元数据
            file_path (Path): 视频文件路径
            format_type (str): 格式类型 ("nfo" 或 "vsmeta")
            season (int): 季数
            episode (int): 集数
        
        返回:
            bool: 生成是否成功
        """
        if format_type == "vsmeta" and self.vsmeta_generator:
            return self.vsmeta_generator.generate_tv_vsmeta(metadata, file_path, season, episode)
        else:
            return self._generate_tv_nfo_xml(metadata, file_path)
    
    def _generate_tv_nfo_xml(self, metadata: TVMetadata, file_path: Path) -> bool:
        """
        生成标准NFO格式的电视剧文件
        
        参数:
            metadata (TVMetadata): 电视剧元数据
            file_path (Path): 视频文件路径
        
        返回:
            bool: 生成是否成功
        """
        try:
            nfo_path = file_path.with_suffix('.nfo')
            
            # 创建XML结构
            tvshow = ET.Element("episodedetails")
            
            # 基本信息
            ET.SubElement(tvshow, "title").text = metadata.title
            if metadata.original_title:
                ET.SubElement(tvshow, "originaltitle").text = metadata.original_title
            if metadata.year:
                ET.SubElement(tvshow, "year").text = str(metadata.year)
            if metadata.first_air_date:
                ET.SubElement(tvshow, "premiered").text = metadata.first_air_date
            if metadata.plot:
                ET.SubElement(tvshow, "plot").text = metadata.plot
            if metadata.creator:
                ET.SubElement(tvshow, "director").text = metadata.creator
            
            # 评分信息
            if metadata.rating_tmdb > 0:
                rating = ET.SubElement(tvshow, "rating")
                rating.set("name", "tmdb")
                rating.set("max", "10")
                ET.SubElement(rating, "value").text = str(metadata.rating_tmdb)
                if metadata.vote_count:
                    ET.SubElement(rating, "votes").text = str(metadata.vote_count)
            
            if metadata.rating_douban > 0:
                rating = ET.SubElement(tvshow, "rating")
                rating.set("name", "douban")
                rating.set("max", "10")
                ET.SubElement(rating, "value").text = str(metadata.rating_douban)
            
            # 类型
            for genre in metadata.genres:
                ET.SubElement(tvshow, "genre").text = genre
            
            # 演员
            for actor_name in metadata.cast:
                actor = ET.SubElement(tvshow, "actor")
                ET.SubElement(actor, "name").text = actor_name
            
            # ID信息
            if metadata.tmdb_id:
                uniqueid = ET.SubElement(tvshow, "uniqueid")
                uniqueid.set("type", "tmdb")
                uniqueid.text = str(metadata.tmdb_id)
            
            if metadata.douban_id:
                uniqueid = ET.SubElement(tvshow, "uniqueid")
                uniqueid.set("type", "douban")
                uniqueid.text = metadata.douban_id
            
            # 写入文件
            tree = ET.ElementTree(tvshow)
            ET.indent(tree, space="  ", level=0)
            tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"生成电视剧NFO文件: {nfo_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"生成电视剧NFO文件失败: {e}")
            return False


class PosterDownloader:
    """
    海报下载器
    
    下载影片海报和背景图
    """
    
    def __init__(self, download_dir: Path):
        """
        初始化海报下载器
        
        参数:
            download_dir (Path): 下载目录
        """
        self.download_dir = download_dir
        self.download_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def download_poster(self, url: str, file_path: Path, poster_type: str = "poster") -> bool:
        """
        下载海报
        
        参数:
            url (str): 海报URL
            file_path (Path): 视频文件路径
            poster_type (str): 海报类型 (poster/fanart)
        
        返回:
            bool: 下载是否成功
        """
        if not url:
            return False
        
        try:
            # 确定海报文件名
            if poster_type == "poster":
                poster_path = file_path.with_name(f"{file_path.stem}-poster.jpg")
            elif poster_type == "fanart":
                poster_path = file_path.with_name(f"{file_path.stem}-fanart.jpg")
            else:
                poster_path = file_path.with_name(f"{file_path.stem}.jpg")
            
            # 如果文件已存在，跳过下载
            if poster_path.exists():
                self.logger.info(f"海报已存在，跳过下载: {poster_path}")
                return True
            
            # 下载海报
            self.logger.info(f"下载海报: {url}")
            
            request = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(poster_path, 'wb') as f:
                    f.write(response.read())
            
            self.logger.info(f"海报下载成功: {poster_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"海报下载失败: {e}")
            return False


class EnhancedVideoRenamer(VideoRenamer):
    """
    增强版视频重命名工具
    
    集成API元数据获取功能
    """
    
    def __init__(self):
        """初始化增强版重命名工具"""
        super().__init__()
        
        # 初始化组件
        self.metadata_fetcher = None
        self.nfo_generator = NFOGenerator()
        self.poster_downloader = None
        
        # 元数据目录
        self.metadata_dir = self.script_dir / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        创建增强版默认配置
        
        返回:
            Dict[str, Any]: 增强版配置字典
        """
        base_config = super()._create_default_config()
        
        # 添加API设置
        base_config["api_settings"] = {
            # TMDb API设置
            "tmdb": {
                "enabled": False,
                "api_key": "",
                "language": "zh-CN",
                "region": "CN",
                "description": "TMDb API用于获取国际影视数据，需要注册获取API密钥"
            },
            
            # 豆瓣API设置
            "douban": {
                "enabled": False,
                "description": "豆瓣API用于获取中文影视数据，无需API密钥但有访问限制"
            },
            
            # API通用设置
            "general": {
                "timeout": 10,
                "retry_count": 3,
                "rate_limit_delay": 1.0,
                "cache_enabled": True,
                "cache_expire_days": 7
            }
        }
        
        # 添加元数据设置
        base_config["metadata_settings"] = {
            "fetch_metadata": True,
            "generate_nfo": True,
            "nfo_format": "vsmeta",  # "nfo" 或 "vsmeta" (群晖Video Station专用)
            "download_posters": True,
            "download_fanart": True,
            "prefer_chinese_title": True,
            "fallback_to_original": True,
            "metadata_priority": ["tmdb", "douban"],
            "poster_size": "w500",
            "fanart_size": "w1280",
            "create_synology_structure": True  # 是否创建群晖标准目录结构
        }
        
        # 增强命名模板
        base_config["naming_templates"]["movie_templates"].update({
            "enhanced_synology": "{chinese_title} {title} ({year}) [{resolution}] [{quality}] [评分{rating}].{ext}",
            "metadata_rich": "{title} ({year}) [TMDb{tmdb_rating}] [豆瓣{douban_rating}] [{resolution}].{ext}",
            "chinese_preferred": "{chinese_title} ({year}) [{resolution}] [{quality}].{ext}"
        })
        
        base_config["naming_templates"]["tv_templates"].update({
            "enhanced_synology": "{chinese_title} {title} S{season:02d}E{episode:02d} [{resolution}] [{quality}] [评分{rating}].{ext}",
            "metadata_rich": "{title} S{season:02d}E{episode:02d} [TMDb{tmdb_rating}] [豆瓣{douban_rating}] [{resolution}].{ext}",
            "chinese_preferred": "{chinese_title} S{season:02d}E{episode:02d} [{resolution}] [{quality}].{ext}"
        })
        
        # 更新版本信息
        base_config["app_info"]["version"] = "2.0.0"
        base_config["app_info"]["name"] = "智能影视文件重命名工具 - 增强版"
        base_config["app_info"]["description"] = "集成TMDb和豆瓣API的智能影视文件重命名工具"
        
        return base_config
    
    def _initialize_components(self) -> None:
        """初始化增强功能组件"""
        if not self.metadata_fetcher:
            self.metadata_fetcher = MetadataFetcher(self.config, self.metadata_dir)
        
        if not self.poster_downloader:
            poster_dir = self.metadata_dir / "posters"
            self.poster_downloader = PosterDownloader(poster_dir)
    
    def _show_config_created_message(self) -> None:
        """显示增强版配置创建消息"""
        print("\n" + "=" * 80)
        print("🎉 智能影视文件重命名工具 - 增强版配置文件创建成功！")
        print("=" * 80)
        print(f"📁 配置文件位置: {self.config_file}")
        print(f"📝 日志文件位置: {self.log_file}")
        print(f"💾 元数据缓存目录: {self.metadata_dir}")
        print(f"💻 当前操作系统: {platform.system()}")
        print("\n🆕 增强版新功能:")
        print("   • TMDb API集成 - 获取国际影视数据")
        print("   • 豆瓣API集成 - 获取中文影视数据")
        print("   • 智能元数据匹配 - 自动选择最佳结果")
        print("   • NFO文件生成 - 媒体中心元数据支持")
        print("   • 海报自动下载 - 完整媒体库体验")
        print("   • 元数据缓存 - 避免重复API调用")
        print("\n⚙️ API配置说明:")
        print("   • TMDb: 需要注册获取免费API密钥")
        print("   • 豆瓣: 无需密钥但有访问频率限制")
        print("   • 建议同时启用两个API获得最佳效果")
        print("\n🔧 配置步骤:")
        print("   1. 访问 https://www.themoviedb.org/settings/api 获取TMDb API密钥")
        print("   2. 在配置文件中设置 api_settings.tmdb.api_key")
        print("   3. 设置 api_settings.tmdb.enabled = true")
        print("   4. 设置 api_settings.douban.enabled = true")
        print("   5. 根据需要调整元数据和命名模板设置")
        print("\n💡 使用建议:")
        print("   1. 首次使用建议启用 dry-run 模式预览")
        print("   2. API调用需要网络连接，处理速度会较慢")
        print("   3. 元数据会自动缓存，重复处理会更快")
        print("   4. 生成的NFO文件可用于Kodi、Jellyfin等媒体中心")
        print("=" * 80)
        print()
    
    def extract_video_info_enhanced(self, filename: str) -> Tuple[VideoInfo, Optional[Union[MovieMetadata, TVMetadata]]]:
        """
        增强版信息提取，集成API元数据
        
        参数:
            filename (str): 文件名
        
        返回:
            Tuple[VideoInfo, Optional[Union[MovieMetadata, TVMetadata]]]: 基础信息和API元数据
        """
        # 先使用基础方法提取信息
        basic_info = self.extract_video_info(filename)
        
        # 检查是否启用元数据获取
        if not self.config.get("metadata_settings", {}).get("fetch_metadata", False):
            return basic_info, None
        
        # 初始化组件
        self._initialize_components()
        
        # 获取API元数据
        api_metadata = None
        if basic_info.title:
            try:
                if basic_info.is_movie:
                    api_metadata = self.metadata_fetcher.fetch_movie_metadata(
                        basic_info.title, 
                        int(basic_info.year) if basic_info.year.isdigit() else None
                    )
                else:
                    api_metadata = self.metadata_fetcher.fetch_tv_metadata(
                        basic_info.title,
                        int(basic_info.year) if basic_info.year.isdigit() else None
                    )
                
                # 使用API数据增强基础信息
                if api_metadata:
                    self._enhance_basic_info(basic_info, api_metadata)
                    
            except Exception as e:
                self.logger.error(f"获取API元数据失败: {e}")
        
        return basic_info, api_metadata
    
    def _enhance_basic_info(self, basic_info: VideoInfo, api_metadata: Union[MovieMetadata, TVMetadata]) -> None:
        """
        使用API元数据增强基础信息
        
        参数:
            basic_info (VideoInfo): 基础视频信息
            api_metadata (Union[MovieMetadata, TVMetadata]): API元数据
        """
        metadata_settings = self.config.get("metadata_settings", {})
        prefer_chinese = metadata_settings.get("prefer_chinese_title", True)
        
        # 更新标题
        if prefer_chinese and api_metadata.chinese_title:
            basic_info.title = api_metadata.chinese_title
        elif api_metadata.title:
            basic_info.title = api_metadata.title
        
        # 更新年份
        if api_metadata.year and not basic_info.year:
            basic_info.year = str(api_metadata.year)
    
    def generate_new_filename_enhanced(self, basic_info: VideoInfo, api_metadata: Optional[Union[MovieMetadata, TVMetadata]] = None) -> str:
        """
        增强版文件名生成，支持API元数据变量
        
        参数:
            basic_info (VideoInfo): 基础视频信息
            api_metadata (Optional[Union[MovieMetadata, TVMetadata]]): API元数据
        
        返回:
            str: 生成的新文件名
        """
        templates = self.config.get('naming_templates', {})
        
        if basic_info.is_movie:
            template_name = templates.get('current_movie_template', 'synology_default')
            template = templates.get('movie_templates', {}).get(template_name, '')
        else:
            template_name = templates.get('current_tv_template', 'synology_default')
            template = templates.get('tv_templates', {}).get(template_name, '')
        
        if not template:
            return self.generate_new_filename(basic_info)
        
        try:
            # 准备基础模板变量
            template_vars = {
                'title': basic_info.title or 'Unknown',
                'year': basic_info.year or '',
                'season': int(basic_info.season) if basic_info.season.isdigit() else 1,
                'episode': int(basic_info.episode) if basic_info.episode.isdigit() else 1,
                'resolution': basic_info.resolution or '',
                'quality': basic_info.quality or '',
                'source': basic_info.source or '',
                'codec': basic_info.codec or '',
                'audio': basic_info.audio or '',
                'language': basic_info.language or '',
                'group': basic_info.group or '',
                'ext': basic_info.extension.lstrip('.')
            }
            
            # 添加API元数据变量
            if api_metadata:
                template_vars.update({
                    'chinese_title': getattr(api_metadata, 'chinese_title', '') or basic_info.title,
                    'original_title': getattr(api_metadata, 'original_title', ''),
                    'tmdb_rating': f"{api_metadata.rating_tmdb:.1f}" if api_metadata.rating_tmdb > 0 else '',
                    'douban_rating': f"{api_metadata.rating_douban:.1f}" if api_metadata.rating_douban > 0 else '',
                    'rating': self._get_best_rating(api_metadata),
                    'director': getattr(api_metadata, 'director', '') or getattr(api_metadata, 'creator', ''),
                    'genre': ', '.join(api_metadata.genres[:2]) if api_metadata.genres else ''
                })
            else:
                # 没有API数据时的默认值
                template_vars.update({
                    'chinese_title': basic_info.title,
                    'original_title': '',
                    'tmdb_rating': '',
                    'douban_rating': '',
                    'rating': '',
                    'director': '',
                    'genre': ''
                })
            
            # 应用模板
            new_name = template.format(**template_vars)
            
            # 清理文件名
            new_name = self._sanitize_filename(new_name)
            
            # 移除空的括号和方括号
            new_name = re.sub(r'\[\s*\]', '', new_name)
            new_name = re.sub(r'\(\s*\)', '', new_name)
            new_name = re.sub(r'\s+', ' ', new_name).strip()
            
            self.logger.debug(f"生成增强文件名: {new_name}")
            return new_name
            
        except Exception as e:
            self.logger.error(f"生成增强文件名时发生错误: {e}")
            return self.generate_new_filename(basic_info)
    
    def _get_best_rating(self, metadata: Union[MovieMetadata, TVMetadata]) -> str:
        """
        获取最佳评分
        
        参数:
            metadata (Union[MovieMetadata, TVMetadata]): 元数据
        
        返回:
            str: 格式化的评分
        """
        if metadata.rating_douban > 0:
            return f"{metadata.rating_douban:.1f}"
        elif metadata.rating_tmdb > 0:
            return f"{metadata.rating_tmdb:.1f}"
        else:
            return ""
    
    def process_file_enhanced(self, file_path: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        增强版文件处理，包含元数据获取和NFO生成
        
        参数:
            file_path (str): 文件路径
            dry_run (bool): 是否为预览模式
        
        返回:
            Dict[str, Any]: 处理结果
        """
        result = {
            'original_path': file_path,
            'success': False,
            'error': None,
            'basic_info': None,
            'api_metadata': None,
            'new_filename': None,
            'nfo_generated': False,
            'poster_downloaded': False
        }
        
        try:
            file_path_obj = Path(file_path)
            filename = file_path_obj.name
            
            # 提取增强信息
            basic_info, api_metadata = self.extract_video_info_enhanced(filename)
            result['basic_info'] = basic_info.to_dict()
            
            if api_metadata:
                result['api_metadata'] = asdict(api_metadata)
            
            # 生成新文件名
            new_filename = self.generate_new_filename_enhanced(basic_info, api_metadata)
            result['new_filename'] = new_filename
            
            if not dry_run:
                new_path = file_path_obj.parent / new_filename
                
                # 重命名文件
                if file_path_obj.name != new_filename:
                    file_path_obj.rename(new_path)
                    self.logger.info(f"文件重命名: {filename} -> {new_filename}")
                else:
                    new_path = file_path_obj
                
                # 生成NFO/vsmeta文件
                if (api_metadata and 
                    self.config.get("metadata_settings", {}).get("generate_nfo", False)):
                    
                    # 获取元数据格式设置
                    nfo_format = self.config.get("metadata_settings", {}).get("nfo_format", "nfo")
                    
                    if basic_info.is_movie:
                        result['nfo_generated'] = self.nfo_generator.generate_movie_nfo(
                            api_metadata, new_path, nfo_format
                        )
                    else:
                        # 提取季集信息
                        season = int(basic_info.season) if basic_info.season.isdigit() else 1
                        episode = int(basic_info.episode) if basic_info.episode.isdigit() else 1
                        
                        result['nfo_generated'] = self.nfo_generator.generate_tv_nfo(
                            api_metadata, new_path, nfo_format, season, episode
                        )
                
                # 下载海报
                if (api_metadata and 
                    self.config.get("metadata_settings", {}).get("download_posters", False)):
                    
                    if api_metadata.poster_url:
                        result['poster_downloaded'] = self.poster_downloader.download_poster(
                            api_metadata.poster_url, new_path, "poster"
                        )
                    
                    # 下载背景图
                    if (api_metadata.backdrop_url and 
                        self.config.get("metadata_settings", {}).get("download_fanart", False)):
                        
                        self.poster_downloader.download_poster(
                            api_metadata.backdrop_url, new_path, "fanart"
                        )
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"处理文件失败 {file_path}: {e}")
        
        return result
    
    def preview_rename_enhanced(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        增强版预览重命名
        
        参数:
            file_paths (List[str]): 文件路径列表
        
        返回:
            List[Dict[str, Any]]: 预览结果列表
        """
        preview_results = []
        
        for file_path in file_paths:
            try:
                file_path_obj = Path(file_path)
                filename = file_path_obj.name
                
                # 提取增强信息
                basic_info, api_metadata = self.extract_video_info_enhanced(filename)
                
                # 生成新文件名
                new_filename = self.generate_new_filename_enhanced(basic_info, api_metadata)
                
                # 构建预览结果
                preview_result = {
                    'original_path': str(file_path),
                    'original_name': filename,
                    'new_name': new_filename,
                    'new_path': str(file_path_obj.parent / new_filename),
                    'type': '电影' if basic_info.is_movie else '电视剧',
                    'title': basic_info.title,
                    'year': basic_info.year,
                    'season': basic_info.season,
                    'episode': basic_info.episode,
                    'resolution': basic_info.resolution,
                    'quality': basic_info.quality,
                    'has_api_data': api_metadata is not None
                }
                
                # 添加API元数据信息
                if api_metadata:
                    preview_result.update({
                        'chinese_title': api_metadata.chinese_title,
                        'original_title': getattr(api_metadata, 'original_title', ''),
                        'tmdb_rating': api_metadata.rating_tmdb if api_metadata.rating_tmdb > 0 else None,
                        'douban_rating': api_metadata.rating_douban if api_metadata.rating_douban > 0 else None,
                        'genres': api_metadata.genres[:3] if api_metadata.genres else [],
                        'director': getattr(api_metadata, 'director', '') or getattr(api_metadata, 'creator', ''),
                        'tmdb_id': api_metadata.tmdb_id,
                        'douban_id': api_metadata.douban_id
                    })
                
                preview_results.append(preview_result)
                
            except Exception as e:
                self.logger.error(f"预览文件 {file_path} 时发生错误: {e}")
                preview_results.append({
                    'original_path': str(file_path),
                    'original_name': Path(file_path).name,
                    'new_name': Path(file_path).name,
                    'new_path': str(file_path),
                    'type': '错误',
                    'error': str(e),
                    'has_api_data': False
                })
        
        return preview_results
    
    def show_enhanced_preview_table(self, preview_results: List[Dict[str, Any]]) -> None:
        """
        显示增强版预览结果表格
        
        参数:
            preview_results (List[Dict[str, Any]]): 预览结果列表
        """
        if not preview_results:
            print("没有找到需要重命名的文件")
            return
        
        print(f"\n{'='*90}")
        print(f"📋 增强版重命名预览结果 (共 {len(preview_results)} 个文件)")
        print(f"{'='*90}")
        
        for i, result in enumerate(preview_results, 1):
            print(f"\n{i:3d}. 【{result.get('type', '未知')}】")
            print(f"     原文件名: {result['original_name']}")
            print(f"     新文件名: {result['new_name']}")
            
            if result.get('has_api_data'):
                print(f"     🌐 API数据: ✅ 已获取")
                
                if result.get('chinese_title'):
                    print(f"     中文标题: {result['chinese_title']}")
                if result.get('original_title'):
                    print(f"     原始标题: {result['original_title']}")
                
                ratings = []
                if result.get('tmdb_rating'):
                    ratings.append(f"TMDb: {result['tmdb_rating']:.1f}")
                if result.get('douban_rating'):
                    ratings.append(f"豆瓣: {result['douban_rating']:.1f}")
                if ratings:
                    print(f"     评分: {' | '.join(ratings)}")
                
                if result.get('genres'):
                    print(f"     类型: {', '.join(result['genres'])}")
                if result.get('director'):
                    print(f"     导演: {result['director']}")
                
                ids = []
                if result.get('tmdb_id'):
                    ids.append(f"TMDb: {result['tmdb_id']}")
                if result.get('douban_id'):
                    ids.append(f"豆瓣: {result['douban_id']}")
                if ids:
                    print(f"     ID: {' | '.join(ids)}")
            else:
                print(f"     🌐 API数据: ❌ 未获取")
            
            # 显示基础信息
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
        
        print(f"\n{'='*90}")
    
    def interactive_mode_enhanced(self) -> None:
        """增强版交互模式"""
        print(f"\n🎬 智能影视文件重命名工具 - 增强版 v{self.config.get('app_info', {}).get('version', '2.0.0')}")
        print(f"   当前操作系统: {platform.system()}")
        print(f"   工作目录: {os.getcwd()}")
        
        # 检查API配置状态
        api_status = self._check_api_status()
        print(f"   API状态: {api_status}")
        
        while True:
            print(f"\n{'='*60}")
            print("请选择操作:")
            print("1. 扫描并预览重命名 (增强版)")
            print("2. 执行重命名 (增强版)")
            print("3. 查看配置信息")
            print("4. 配置API设置")
            print("5. 测试API连接")
            print("6. 清理元数据缓存")
            print("7. 帮助信息")
            print("8. 退出")
            print(f"{'='*60}")
            
            try:
                choice = input("请输入选择 (1-8): ").strip()
                
                if choice == '1':
                    self._handle_enhanced_preview_mode()
                elif choice == '2':
                    self._handle_enhanced_rename_mode()
                elif choice == '3':
                    self._show_enhanced_config_info()
                elif choice == '4':
                    self._handle_api_configuration()
                elif choice == '5':
                    self._test_api_connections()
                elif choice == '6':
                    self._clean_metadata_cache()
                elif choice == '7':
                    self._show_enhanced_help()
                elif choice == '8':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请输入 1-8")
                    
            except KeyboardInterrupt:
                print(f"\n\n👋 程序已退出")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                self.logger.error(f"交互模式错误: {e}")
    
    def _check_api_status(self) -> str:
        """
        检查API配置状态
        
        返回:
            str: API状态描述
        """
        api_settings = self.config.get("api_settings", {})
        
        tmdb_enabled = api_settings.get("tmdb", {}).get("enabled", False)
        tmdb_key = api_settings.get("tmdb", {}).get("api_key", "")
        douban_enabled = api_settings.get("douban", {}).get("enabled", False)
        
        status_parts = []
        
        if tmdb_enabled and tmdb_key:
            status_parts.append("TMDb✅")
        elif tmdb_enabled:
            status_parts.append("TMDb❌(无密钥)")
        else:
            status_parts.append("TMDb❌")
        
        if douban_enabled:
            status_parts.append("豆瓣✅")
        else:
            status_parts.append("豆瓣❌")
        
        return " | ".join(status_parts)
    
    def _handle_enhanced_preview_mode(self) -> None:
        """处理增强版预览模式"""
        directory = input("请输入要扫描的目录路径 (回车使用当前目录): ").strip()
        if not directory:
            directory = os.getcwd()
        
        print(f"🔍 正在扫描目录: {directory}")
        file_paths = self.scan_directory(directory)
        
        if not file_paths:
            print("❌ 未找到视频文件")
            return
        
        print(f"✅ 找到 {len(file_paths)} 个视频文件")
        
        # 询问是否获取API数据
        if self._check_api_available():
            fetch_api = input("是否获取API元数据？(Y/n): ").strip().lower()
            if fetch_api in ['n', 'no']:
                # 临时禁用API
                original_setting = self.config.get("metadata_settings", {}).get("fetch_metadata", True)
                self.config["metadata_settings"]["fetch_metadata"] = False
        
        try:
            # 生成增强预览
            print("🌐 正在获取元数据，请稍候...")
            preview_results = self.preview_rename_enhanced(file_paths)
            self.show_enhanced_preview_table(preview_results)
            
        finally:
            # 恢复API设置
            if 'original_setting' in locals():
                self.config["metadata_settings"]["fetch_metadata"] = original_setting
    
    def _handle_enhanced_rename_mode(self) -> None:
        """处理增强版重命名模式"""
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
        print("🌐 正在生成预览，请稍候...")
        preview_results = self.preview_rename_enhanced(file_paths)
        self.show_enhanced_preview_table(preview_results)
        
        # 确认执行
        confirm = input(f"\n⚠️  确定要重命名这 {len(file_paths)} 个文件吗？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        # 执行增强重命名
        print("🚀 开始增强重命名...")
        success_count = 0
        error_count = 0
        
        for file_path in file_paths:
            try:
                result = self.process_file_enhanced(file_path, dry_run=False)
                if result['success']:
                    success_count += 1
                    print(f"✅ {Path(file_path).name}")
                    
                    if result.get('nfo_generated'):
                        print(f"   📄 NFO文件已生成")
                    if result.get('poster_downloaded'):
                        print(f"   🖼️ 海报已下载")
                else:
                    error_count += 1
                    print(f"❌ {Path(file_path).name}: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ {Path(file_path).name}: {e}")
        
        # 显示结果
        print(f"\n📊 增强重命名完成:")
        print(f"   成功: {success_count}")
        print(f"   失败: {error_count}")
        print(f"   总计: {len(file_paths)}")
    
    def _check_api_available(self) -> bool:
        """检查是否有可用的API"""
        api_settings = self.config.get("api_settings", {})
        
        tmdb_available = (api_settings.get("tmdb", {}).get("enabled", False) and 
                         api_settings.get("tmdb", {}).get("api_key", ""))
        douban_available = api_settings.get("douban", {}).get("enabled", False)
        
        return tmdb_available or douban_available
    
    def _show_enhanced_config_info(self) -> None:
        """显示增强版配置信息"""
        print(f"\n📋 增强版配置信息:")
        print(f"   应用版本: {self.config.get('app_info', {}).get('version', '未知')}")
        print(f"   配置文件: {self.config_file}")
        print(f"   元数据目录: {self.metadata_dir}")
        
        # API配置状态
        api_settings = self.config.get("api_settings", {})
        print(f"\n🌐 API配置:")
        
        tmdb_config = api_settings.get("tmdb", {})
        print(f"   TMDb: {'启用' if tmdb_config.get('enabled') else '禁用'}")
        if tmdb_config.get("enabled"):
            has_key = bool(tmdb_config.get("api_key"))
            print(f"   TMDb API密钥: {'已配置' if has_key else '未配置'}")
        
        douban_config = api_settings.get("douban", {})
        print(f"   豆瓣: {'启用' if douban_config.get('enabled') else '禁用'}")
        
        # 元数据设置
        metadata_settings = self.config.get("metadata_settings", {})
        print(f"\n📄 元数据设置:")
        print(f"   获取元数据: {'启用' if metadata_settings.get('fetch_metadata') else '禁用'}")
        print(f"   生成NFO: {'启用' if metadata_settings.get('generate_nfo') else '禁用'}")
        print(f"   下载海报: {'启用' if metadata_settings.get('download_posters') else '禁用'}")
        print(f"   优先中文标题: {'是' if metadata_settings.get('prefer_chinese_title') else '否'}")
    
    def _handle_api_configuration(self) -> None:
        """处理API配置"""
        print(f"\n⚙️ API配置管理:")
        print("1. 配置TMDb API")
        print("2. 启用/禁用豆瓣API")
        print("3. 元数据设置")
        print("4. 返回主菜单")
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == '1':
            self._configure_tmdb_api()
        elif choice == '2':
            self._toggle_douban_api()
        elif choice == '3':
            self._configure_metadata_settings()
        elif choice == '4':
            return
        else:
            print("❌ 无效选择")
    
    def _configure_tmdb_api(self) -> None:
        """配置TMDb API"""
        print(f"\n🔧 TMDb API配置:")
        print("1. 获取API密钥: https://www.themoviedb.org/settings/api")
        print("2. 注册免费账户并申请API密钥")
        print("3. 将API密钥粘贴到下方")
        
        current_key = self.config.get("api_settings", {}).get("tmdb", {}).get("api_key", "")
        if current_key:
            print(f"当前API密钥: {current_key[:8]}...")
        
        new_key = input("请输入TMDb API密钥 (回车保持不变): ").strip()
        
        if new_key:
            if "api_settings" not in self.config:
                self.config["api_settings"] = {}
            if "tmdb" not in self.config["api_settings"]:
                self.config["api_settings"]["tmdb"] = {}
            
            self.config["api_settings"]["tmdb"]["api_key"] = new_key
            self.config["api_settings"]["tmdb"]["enabled"] = True
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            print("✅ TMDb API配置已保存")
        
        # 询问是否测试连接
        if new_key or current_key:
            test = input("是否测试API连接？(y/N): ").strip().lower()
            if test == 'y':
                self._test_tmdb_connection()
    
    def _toggle_douban_api(self) -> None:
        """切换豆瓣API状态"""
        current_state = self.config.get("api_settings", {}).get("douban", {}).get("enabled", False)
        new_state = not current_state
        
        if "api_settings" not in self.config:
            self.config["api_settings"] = {}
        if "douban" not in self.config["api_settings"]:
            self.config["api_settings"]["douban"] = {}
        
        self.config["api_settings"]["douban"]["enabled"] = new_state
        
        # 保存配置
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 豆瓣API已{'启用' if new_state else '禁用'}")
        
        if new_state:
            print("⚠️  注意: 豆瓣API有访问频率限制，请适度使用")
    
    def _configure_metadata_settings(self) -> None:
        """配置元数据设置"""
        metadata_settings = self.config.get("metadata_settings", {})
        
        print(f"\n📄 元数据设置:")
        print(f"1. 获取元数据: {'启用' if metadata_settings.get('fetch_metadata') else '禁用'}")
        print(f"2. 生成NFO文件: {'启用' if metadata_settings.get('generate_nfo') else '禁用'}")
        print(f"3. 下载海报: {'启用' if metadata_settings.get('download_posters') else '禁用'}")
        print(f"4. 优先中文标题: {'是' if metadata_settings.get('prefer_chinese_title') else '否'}")
        print("5. 返回")
        
        choice = input("请选择要切换的设置 (1-5): ").strip()
        
        settings_map = {
            '1': 'fetch_metadata',
            '2': 'generate_nfo',
            '3': 'download_posters',
            '4': 'prefer_chinese_title'
        }
        
        if choice in settings_map:
            setting_key = settings_map[choice]
            current_value = metadata_settings.get(setting_key, False)
            new_value = not current_value
            
            self.config["metadata_settings"][setting_key] = new_value
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            setting_names = {
                'fetch_metadata': '获取元数据',
                'generate_nfo': '生成NFO文件',
                'download_posters': '下载海报',
                'prefer_chinese_title': '优先中文标题'
            }
            
            print(f"✅ {setting_names[setting_key]}已{'启用' if new_value else '禁用'}")
        elif choice == '5':
            return
        else:
            print("❌ 无效选择")
    
    def _test_api_connections(self) -> None:
        """测试API连接"""
        print(f"\n🔗 测试API连接...")
        
        # 初始化组件
        self._initialize_components()
        
        # 测试TMDb
        if self.metadata_fetcher.tmdb_client:
            self._test_tmdb_connection()
        else:
            print("❌ TMDb API未配置")
        
        # 测试豆瓣
        if self.metadata_fetcher.douban_client:
            self._test_douban_connection()
        else:
            print("❌ 豆瓣API未启用")
    
    def _test_tmdb_connection(self) -> None:
        """测试TMDb连接"""
        try:
            print("🔍 测试TMDb连接...")
            
            if not self.metadata_fetcher:
                self._initialize_components()
            
            if not self.metadata_fetcher.tmdb_client:
                print("❌ TMDb客户端未初始化")
                return
            
            # 搜索一个知名电影
            results = self.metadata_fetcher.tmdb_client.search_movie("The Matrix", 1999)
            
            if results:
                print(f"✅ TMDb连接成功，找到 {len(results)} 个结果")
                if results[0].get('title'):
                    print(f"   示例结果: {results[0]['title']} ({results[0].get('release_date', '')[:4]})")
            else:
                print("❌ TMDb连接失败或无结果")
                
        except Exception as e:
            print(f"❌ TMDb连接测试失败: {e}")
    
    def _test_douban_connection(self) -> None:
        """测试豆瓣连接"""
        try:
            print("🔍 测试豆瓣连接...")
            
            if not self.metadata_fetcher:
                self._initialize_components()
            
            if not self.metadata_fetcher.douban_client:
                print("❌ 豆瓣客户端未初始化")
                return
            
            # 搜索一个知名电影
            results = self.metadata_fetcher.douban_client.search_movie("肖申克的救赎")
            
            if results:
                print(f"✅ 豆瓣连接成功，找到 {len(results)} 个结果")
                if results[0].get('title'):
                    print(f"   示例结果: {results[0]['title']}")
            else:
                print("❌ 豆瓣连接失败或无结果")
                
        except Exception as e:
            print(f"❌ 豆瓣连接测试失败: {e}")
    
    def _clean_metadata_cache(self) -> None:
        """清理元数据缓存"""
        try:
            cache_file = self.metadata_dir / "metadata_cache.json"
            if cache_file.exists():
                cache_file.unlink()
                print("✅ 元数据缓存已清理")
            else:
                print("ℹ️  没有找到缓存文件")
                
        except Exception as e:
            print(f"❌ 清理缓存失败: {e}")
    
    def _show_enhanced_help(self) -> None:
        """显示增强版帮助信息"""
        print(f"\n📖 增强版帮助信息:")
        print(f"{'='*70}")
        print("🎯 增强功能说明:")
        print("   • TMDb API集成 - 获取国际影视数据库信息")
        print("   • 豆瓣API集成 - 获取中文影视数据")
        print("   • 智能匹配算法 - 自动选择最佳匹配结果")
        print("   • NFO文件生成 - 支持Kodi、Jellyfin等媒体中心")
        print("   • 海报自动下载 - 完整的媒体库体验")
        print("   • 元数据缓存 - 避免重复API调用")
        
        print(f"\n🔧 API配置说明:")
        print("   TMDb API:")
        print("   1. 访问 https://www.themoviedb.org/settings/api")
        print("   2. 注册免费账户")
        print("   3. 申请API密钥")
        print("   4. 在程序中配置API密钥")
        
        print(f"\n   豆瓣API:")
        print("   • 无需注册，直接启用即可")
        print("   • 有访问频率限制，请适度使用")
        print("   • 主要用于获取中文标题和评分")
        
        print(f"\n📝 增强模板变量:")
        print("   {chinese_title} - 中文标题")
        print("   {original_title} - 原始标题")
        print("   {tmdb_rating} - TMDb评分")
        print("   {douban_rating} - 豆瓣评分")
        print("   {rating} - 最佳评分")
        print("   {director} - 导演")
        print("   {genre} - 类型")
        
        print(f"\n💡 使用建议:")
        print("   1. 首次使用建议配置TMDb API获得最佳效果")
        print("   2. 启用元数据缓存可以提高重复处理速度")
        print("   3. NFO文件和海报可以提升媒体中心体验")
        print("   4. 网络连接不稳定时可以禁用API功能")
        print("   5. 大批量处理时建议分批进行")
        print(f"{'='*70}")
    
    def run(self) -> None:
        """
        运行增强版程序
        """
        try:
            # 加载配置
            if not self.load_config():
                print("❌ 配置加载失败，程序无法继续运行")
                return
            
            # 启动增强版交互模式
            self.interactive_mode_enhanced()
            
        except Exception as e:
            self.logger.error(f"程序运行失败: {e}")
            print(f"❌ 程序运行失败: {e}")
        
        finally:
            self.logger.info("智能影视文件重命名工具 - 增强版结束")


def main():
    """
    程序主函数
    """
    print("🎬 智能影视文件重命名工具 - 增强版")
    print("   支持平台: Windows、macOS、群晖NAS")
    print("   集成API: TMDb、豆瓣")
    print("   作者: OpenHands AI")
    
    # 创建增强版应用实例
    renamer = EnhancedVideoRenamer()
    
    # 运行应用
    renamer.run()


# 程序入口点
if __name__ == "__main__":
    main()