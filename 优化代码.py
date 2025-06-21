#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电视剧文件整理工具专业版 V2.7 - 优化性能与增强功能
"""
import os
import re
import sys
import json
import yaml
import logging
import argparse
import shutil
import time
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Optional, Dict, List, Any, Tuple, Set
import threading
import random
import xml.etree.ElementTree as ET

from jinja2 import Template
from colorama import Fore, Style, init as colorama_init
from tqdm import tqdm
from anytree import Node, RenderTree

colorama_init(autoreset=True)

# ========================= 配置管理系统 =========================
class ConfigManager:
    """支持热加载和自动生成的配置管理系统"""

    DEFAULT_CONFIG = '''# 电视剧整理工具配置文件 V2.7
version: "2.7"
paths:
    tv_shows: './电视剧待整理'
    backup: './电视剧待整理/备份'
    output: './电视剧整理完成'
    undo_log: 'undo_log.json'
    log_dir: 'logs'
    checkpoint: 'checkpoint.json'
    report_dir: 'reports'
    hash_cache: '.file_hashes.json'

rules:
    extensions: ['.mp4', '.mkv', '.avi', '.ts', '.mov', '.flv', '.wmv']
    metadata_extensions: ['.nfo', '.srt', '.ass', '.ssa', '.vsmeta', '.jpg', '.png']
    min_size_mb: 50
    recursive: true
    process_nested: true
    exclude_keywords: ['sample', 'trailer', 'temp', '预告']
    exclude_dirs: ['@eaDir', 'extras', 'sample', 'temp']
    preview_only: true
    hot_reload: true
    show_tree: true
    title_clean_rules: [
        {'pattern': r'\\.\d{4}$', 'replacement': ''},
        {'pattern': r'_+', 'replacement': ' '},
        {'pattern': r'[^\\u4e00-\\u9fffa-zA-Z0-9\\.]', 'replacement': '.'}
    ]
    season_priority: ['directory', 'filename', 'smart']
    max_retry: 3
    ngram_threshold: 0.7
    incremental_processing: true
    hash_cache_size: 10000

patterns:
    title_season: [
        {'pattern': r'^(.+?)(?:\\.\\d{4})?\\.(S\\d+)', 'description': '标准季数格式: S01'},
        {'pattern': r'^(.+?)\\s+(?:Season|Saison)\\s*(\\d+)', 'description': '西式季数格式: Season 1'},
        {'pattern': r'^(.+?)\\s+第(\\d+)季', 'description': '中文季数格式: 第1季'}
    ]
    episode: [
        {'pattern': r'E(\\d{1,3})', 'description': 'E格式集数: E01'},
        {'pattern': r'EP(\\d{1,3})', 'description': 'EP格式集数: EP01'},
        {'pattern': r'\\[第?(\\d{1,3})[集话]\\]', 'description': '方括号集数: [01]'}
    ]

naming:
    pattern: '{title}.S{season:02d}.E{episode:02d}{ext}'
    dir_pattern: '{title}/Season {season:02d}'
    season_as_dir: true

report:
    enabled: true
    template: |
        <!DOCTYPE html>
        <html>
        <head>
            <title>电视剧整理报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ color: #2c3e50; }}
                .details {{ color: #3498db; margin-left: 20px; }}
                .error {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <h1>电视剧整理报告</h1>
            <p>生成时间: {{ timestamp }}</p>
            <div class="summary">
                <h2>操作统计</h2>
                <p>总处理文件: {{ stats.processed }}</p>
                <p>成功移动: {{ stats.moved }}</p>
                <p>备份文件: {{ stats.backups }}</p>
                <p>元数据同步: {{ stats.meta_moved }}</p>
                <p>错误数量: {{ stats.errors }}</p>
            </div>
            <div class="details">
                <h2>详细日志</h2>
                {% for log in logs %}
                <p>{{ log }}</p>
                {% endfor %}
            </div>
        </body>
        </html>
    '''

    @classmethod
    def load_config(cls, config_path: str = None):
        """加载配置文件（支持默认配置生成）"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return yaml.safe_load(cls.DEFAULT_CONFIG)

    @classmethod
    def _precompile_patterns(cls, patterns):
        """预编译所有正则表达式模式（性能优化）"""
        return {p['pattern']: re.compile(p['pattern'], re.IGNORECASE) for p in patterns}

# ========================= 核心处理器 =========================
class TVShowProcessor:
    def __init__(self, config_path: str = None):
        self.config_path = config_path  # 修正
        self.config = ConfigManager.load_config(config_path)
        self.regex_cache = ConfigManager._precompile_patterns(
            self.config['patterns']['title_season'] + self.config['patterns']['episode']
        )
        self.file_hashes = self._load_hash_cache()
        self.executor = ProcessPoolExecutor(max_workers=os.cpu_count()*2)
        self.lock = threading.Lock()
        self.counters = {
            'processed': 0,
            'moved': 0,
            'skipped': 0,
            'errors': 0,
            'backups': 0,
            'meta_moved': 0,
            'recovered': 0
        }
        self._init_components()
        self._verify_paths()
        self._ensure_required_files()
        self.last_config_mtime = 0

    def _init_components(self):
        self._init_logger()
        # self._init_matchers() # 可选扩展
        self._preload_regex_patterns()
        self._init_report_template()

    def _preload_regex_patterns(self):
        """预加载所有正则表达式到缓存（已完成）"""
        pass

    def _init_report_template(self):
        self.report_template = Template(self.config['report']['template'])

    def _verify_paths(self):
        required_paths = ['tv_shows', 'output']
        for path_key in required_paths:
            path = self.config['paths'].get(path_key, '')
            if not path:
                raise ValueError(f"必须配置路径: {path_key}")
            if not os.path.exists(path):
                print(f"{Fore.YELLOW}警告: 路径不存在 - {path_key}: {path}")
                if path_key == 'tv_shows':
                    raise RuntimeError("源目录不存在，程序终止")

    def _ensure_required_files(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))

        log_dir = self.config['paths'].get('log_dir', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        undo_log = self.config['paths'].get('undo_log', 'undo_log.json')
        if not os.path.exists(undo_log):
            with open(undo_log, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        checkpoint = self.config['paths'].get('checkpoint', 'checkpoint.json')
        if not os.path.exists(checkpoint):
            with open(checkpoint, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        report_dir = self.config['paths'].get('report_dir', 'reports')
        os.makedirs(report_dir, exist_ok=True)

    def _init_logger(self):
        log_dir = self.config['paths'].get('log_dir', 'logs')
        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger('TVShowPro')
        self.logger.setLevel(logging.INFO)
        fmt_text = '%(asctime)s [%(levelname)s] %(message)s'
        fmt_json = '{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
        date_fmt = '%Y-%m-%d %H:%M:%S'

        log_file = os.path.join(log_dir, f"process_{datetime.now().strftime('%Y%m%d')}.log")
        json_log_file = os.path.join(log_dir, f"process_{datetime.now().strftime('%Y%m%d')}.json.log")

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(fmt_text, date_fmt))

        json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
        json_handler.setFormatter(logging.Formatter(fmt_json, date_fmt))

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt_text, date_fmt))

        # 防止重复添加 handler
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(json_handler)
            self.logger.addHandler(console_handler)

        self.logger.info("="*50)
        self.logger.info(" 电视剧整理工具启动（V2.7）")
        self.logger.info(f" 配置文件: {self.config_path or '默认配置'}")

    def _check_hot_reload(self):
        if self.config['rules'].get('hot_reload') and self.config_path:
            try:
                mtime = os.path.getmtime(self.config_path)
                if hasattr(self, 'last_config_mtime') and mtime > self.last_config_mtime:
                    self.logger.info(" 检测到配置文件变更，正在热重载...")
                    new_config = ConfigManager.load_config(self.config_path)
                    old_counters = self.counters.copy()
                    self.config = new_config
                    self._init_components()
                    self.counters.update(old_counters)
                    self.last_config_mtime = mtime
                    self.logger.info(' 配置热重载成功')
                    print(f"{Fore.CYAN}配置已热重载")
            except Exception as e:
                self.logger.error(f" 配置热重载失败: {e}")

    def process(self, preview: Optional[bool] = None):
        """核心处理流程（增强版）"""
        self._check_hot_reload()
        preview = preview if preview is not None else self.config['rules']['preview_only']
        root = self.config['paths']['tv_shows']

        if not os.path.exists(root):
            raise FileNotFoundError(f"源目录不存在: {root}")

        if self.config['rules']['show_tree']:
            print(f"\n{Fore.CYAN}【原始目录结构】{root}")
            print(self._generate_tree_view(root))

        print(f"\n{Fore.CYAN}开始处理: {'预览模式' if preview else '执行模式'}")
        self.logger.info(f" 处理模式: {'预览' if preview else '执行'}")

        processed = self._load_checkpoint()
        all_files = self._collect_files(root, processed)

        conflict_files = self._scan_conflicts(all_files, preview)
        if conflict_files:
            self.logger.warning(f" 检测到{len(conflict_files)}个同名文件冲突，处理前请确认!")
            for src, dest in conflict_files.items():
                print(f"{Fore.YELLOW} 冲突: {os.path.basename(src)} → {dest}")

        with tqdm(total=len(all_files), desc="处理进度", unit="文件",
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            for filepath in all_files:
                try:
                    self._process_single_file(filepath, preview)
                    processed.add(filepath)
                    self._save_checkpoint(processed)
                except Exception as e:
                    self.logger.error(f" 处理失败: {filepath} - {e}", exc_info=True)
                    self.counters['errors'] += 1
                finally:
                    pbar.update(1)

        if self.config['report']['enabled']:
            self._generate_html_report()

        self._show_results(preview)

    def _collect_files(self, root: str, processed: set) -> list:
        """高效递归收集有效文件（支持增量处理、跳过已处理）"""
        valid_exts = tuple(self.config['rules']['extensions'])
        exclude_dirs = set(self.config['rules']['exclude_dirs'])
        exclude_keywords = set(self.config['rules']['exclude_keywords'])
        min_size = self.config['rules']['min_size_mb'] * 1024 * 1024
        recursive = self.config['rules']['recursive']

        all_files = []
        def _walk(d):
            with os.scandir(d) as it:
                for entry in it:
                    if entry.is_dir():
                        if entry.name in exclude_dirs:
                            continue
                        if recursive:
                            _walk(entry.path)
                    elif entry.is_file():
                        if not entry.name.lower().endswith(valid_exts):
                            continue
                        if any(k in entry.name.lower() for k in exclude_keywords):
                            continue
                        if entry.stat().st_size < min_size:
                            continue
                        if self.config['rules'].get('incremental_processing'):
                            if entry.path in processed:
                                continue
                        all_files.append(entry.path)
        _walk(root)
        return all_files

    def _load_hash_cache(self):
        cache_file = self.config['paths'].get('hash_cache', '.file_hashes.json')
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _scan_conflicts(self, all_files: List[str], preview: bool) -> Dict[str, str]:
        conflicts = {}
        output_dir = self.config['paths']['output']
        for filepath in all_files:
            info = self.extract_info(filepath)
            if not info:
                continue
            new_path = self._build_output_path(info)
            if os.path.exists(new_path):
                conflicts[filepath] = new_path
        return conflicts

    def _generate_html_report(self):
        report_dir = self.config['paths'].get('report_dir', 'reports')
        report_path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html")
        logs = [
            f"{Fore.GREEN}处理完成: 总文件数={self.counters['processed']}",
            f"成功移动: {self.counters['moved']}, 备份文件: {self.counters['backups']}",
            f"元数据同步: {self.counters['meta_moved']}, 错误数量: {self.counters['errors']}"
        ]
        html_content = self.report_template.render(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            stats=self.counters,
            logs=logs
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        self.logger.info(f" HTML报告已生成: {report_path}")

    def _build_output_path(self, info: Dict) -> str:
        dir_pattern = self.config['naming']['dir_pattern'].format(
            title=info['title'],
            season=info['season']
        )
        file_pattern = self.config['naming']['pattern'].format(
            title=info['title'],
            season=info['season'],
            episode=info['episode'],
            ext=info['ext']
        )
        return os.path.join(self.config['paths']['output'], dir_pattern, file_pattern)

    def _process_single_file(self, filepath: str, preview: bool):
        self.counters['processed'] += 1
        info = self.extract_info(filepath)
        if not info:
            self.counters['skipped'] += 1
            self.logger.warning(f" 无法解析: {os.path.basename(filepath)}")
            return

        meta_files = self._get_associated_metadata(filepath)
        for attempt in range(self.config['rules']['max_retry']):
            try:
                self._move_file_with_retry(filepath, info, preview, meta_files)
                break
            except Exception as e:
                if attempt == self.config['rules']['max_retry'] - 1:
                    raise RuntimeError(f"最终移动失败: {e}")
                self.logger.warning(f" 第{attempt+1}次尝试失败，重试中...: {e}")
                time.sleep(1)

    def _move_file_with_retry(self, src: str, info: Dict, preview: bool, meta_files: List[str]):
        new_path = self._build_output_path(info)
        base_src = os.path.splitext(src)[0]
        new_base = os.path.splitext(new_path)[0]
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        if preview:
            rel_path = os.path.relpath(new_path, self.config['paths']['output'])
            print(f"{Fore.GREEN}预览: {os.path.basename(src)} → {rel_path}")
            self.logger.info(f" 预览移动: {src} → {new_path}")
            for meta in meta_files:
                meta_rel = os.path.relpath(meta, os.path.dirname(src))
                meta_dest = os.path.join(os.path.dirname(new_path), os.path.basename(meta))
                print(f"  预览元数据: {os.path.basename(meta)} → {os.path.basename(meta_dest)}")
            return

        if self._backup_file(src):
            self.counters['backups'] += 1

        for attempt in range(self.config['rules']['max_retry']):
            try:
                shutil.move(src, new_path)
                self._record_undo_action(src, new_path)
                print(f"{Fore.YELLOW}已移动: {os.path.basename(src)} → {os.path.basename(new_path)}")
                self.logger.info(f" 移动完成: {src} → {new_path}")
                self.counters['moved'] += 1
                break
            except PermissionError as e:
                if attempt < self.config['rules']['max_retry'] - 1:
                    time.sleep(1)
                    continue
                raise RuntimeError(f"权限不足: {e}")
            except OSError as e:
                if "另一个程序正在使用此文件" in str(e):
                    raise RuntimeError(f"文件被占用: {src}（请关闭相关进程后重试）")
                else:
                    raise

        if meta_files:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for meta in meta_files:
                    meta_dest = f"{new_base}{os.path.splitext(meta)[1]}"
                    futures.append(executor.submit(
                        self._move_metadata_file, meta, meta_dest, preview, info
                    ))
                for future in futures:
                    future.result()

    def _move_metadata_file(self, src_meta: str, dest_meta: str, preview: bool, info: dict = None):
        if preview:
            print(f"  预览元数据移动: {os.path.basename(src_meta)} → {os.path.basename(dest_meta)}")
            return

        try:
            if self._backup_file(src_meta):
                self.counters['backups'] += 1
            shutil.move(src_meta, dest_meta)
            self._record_undo_action(src_meta, dest_meta)
            self.counters['meta_moved'] += 1
            self.logger.info(f" 移动元数据: {os.path.basename(src_meta)} → {os.path.basename(dest_meta)}")
            if src_meta.lower().endswith('.nfo'):
                self._update_nfo_metadata(dest_meta, info)
        except Exception as e:
            self.logger.error(f" 元数据移动失败: {src_meta} - {e}")

    def _update_nfo_metadata(self, nfo_path: str, info: dict):
        """可选：自动更新nfo元数据内容，提升媒体库兼容性"""
        # 简单示例：加个注释节点，不做复杂解析
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()
            comment = ET.Comment(f"Processed by TVShowPro at {datetime.now().isoformat()}")
            root.insert(0, comment)
            tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
        except Exception:
            pass

    def extract_info(self, filepath: str) -> Optional[Dict]:
        filename = os.path.basename(filepath)
        basename, ext = os.path.splitext(filename)
        dirname = os.path.basename(os.path.dirname(filepath))

        dir_priority = self.config['rules']['season_priority']
        for source in dir_priority:
            if source == 'directory':
                dir_info = self._extract_from_directory(dirname)
                if dir_info:
                    title, season = dir_info
                    title = self._clean_title(title)
                    episode = self._extract_episode(basename)
                    if episode is not None:
                        return {
                            'title': title,
                            'season': season,
                            'episode': episode,
                            'ext': ext
                        }
        file_info = self._extract_from_filename(basename)
        if file_info:
            title, season = file_info
            title = self._clean_title(title)
            episode = self._extract_episode(basename)
            if episode is not None:
                return {
                    'title': title,
                    'season': season,
                    'episode': episode,
                    'ext': ext
                }
        smart_priority = self.config['rules']['season_priority']
        for source in smart_priority:
            if source == 'smart':
                smart_info = self._smart_supplement(filepath, basename, dirname)
                if smart_info:
                    title, season, episode = smart_info
                    title = self._clean_title(title)
                    return {
                        'title': title,
                        'season': season,
                        'episode': episode,
                        'ext': ext
                    }
        self.logger.warning(f" 无法解析: {filename}")
        return None

    def _extract_episode(self, basename: str) -> Optional[int]:
        for pattern in self.config['patterns']['episode']:
            match = self.regex_cache[pattern['pattern']].search(basename)
            if match:
                return self._parse_episode_number(match.group(1))
        return 1  # 默认第一集

    def _clean_title(self, raw_title: str) -> str:
        for rule in self.config['rules']['title_clean_rules']:
            pattern = re.compile(rule['pattern'])
            raw_title = pattern.sub(rule['replacement'], raw_title)
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', raw_title)
        if chinese_chars:
            cleaned = ''.join(chinese_chars).strip()
            en_suffix = re.sub(r'[\u4e00-\u9fff]+', '', raw_title).strip()
            if en_suffix:
                cleaned += f" {en_suffix}"
            return cleaned
        return raw_title.strip()

    def _extract_from_directory(self, dirname: str) -> Optional[Tuple[str, int]]:
        for pattern in self.config['patterns']['title_season']:
            match = self.regex_cache[pattern['pattern']].match(dirname)
            if match:
                title_part = match.group(1).replace('.', ' ').strip()
                season_part = match.group(2) if len(match.groups()) > 1 else None
                if season_part and season_part.isdigit() and len(season_part) == 4:
                    season = 1
                else:
                    season = self._parse_season_number(season_part) if season_part else None
                return (title_part, season)
        return None

    def _extract_from_filename(self, basename: str) -> Optional[Tuple[str, int]]:
        for pattern in self.config['patterns']['title_season']:
            match = self.regex_cache[pattern['pattern']].match(basename)
            if match:
                title_part = match.group(1).replace('.', ' ').strip()
                season_part = match.group(2) if len(match.groups()) > 1 else None
                season = self._parse_season_number(season_part) if season_part else None
                return (title_part, season)
        return None

    def _smart_supplement(self, filepath: str, basename: str, dirname: str) -> Optional[Tuple[str, int, int]]:
        year_match = re.search(r'\.(\d{4})$', dirname)
        year = year_match.group(1) if year_match else None
        title_match = re.match(r'^(.+?)(?:\.\d{4})?(?:[\. \-_]*[Ss]?\d+)?(?:[\. \-_]*[Ee]?\d+)?', basename)
        if not title_match:
            return None
        title = title_match.group(1).replace('.', ' ').strip()
        title = self._clean_title(title)
        season = 1
        if year:
            season = 1
        elif any(re.search(r'[Ss]\d+', basename, re.IGNORECASE) for _ in self.config['patterns']['title_season']):
            pass
        else:
            season = 1
        episode = 1
        ep_match = re.search(r'[Ee](\d+)', basename)
        if ep_match:
            episode = self._parse_episode_number(ep_match.group(1))
        return (title, season, episode)

    def _get_associated_metadata(self, filepath: str) -> List[str]:
        base_name = os.path.splitext(filepath)[0]
        extensions = self.config['rules']['metadata_extensions']
        return [
            f"{base_name}{ext}" 
            for ext in extensions
            if os.path.exists(f"{base_name}{ext}")
        ]

    def _parse_season_number(self, s: str) -> Optional[int]:
        cn_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14,
            '十五': 15, '十六': 16, '十七': 17, '十八': 18,
            '十九': 19, '二十': 20, '廿': 20, '卅': 30
        }
        if s in cn_numbers:
            return cn_numbers[s]
        try:
            return int(s.lstrip('Ss'))
        except Exception:
            return None

    def _parse_episode_number(self, s: str) -> Optional[int]:
        cn_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14,
            '十五': 15, '十六': 16, '十七': 17, '十八': 18,
            '十九': 19, '二十': 20, '廿': 20, '卅': 30
        }
        if s in cn_numbers:
            return cn_numbers[s]
        try:
            return int(s)
        except Exception:
            return None

    def _record_undo_action(self, original: str, new_path: str):
        if not self.config['paths'].get('undo_log'):
            return
        entry = {
            'timestamp': datetime.now().isoformat(),
            'original': original,
            'new_path': new_path,
            'type': 'file' if original == new_path.replace('.bak', '') else 'metadata'
        }
        history = []
        undo_log = self.config['paths'].get('undo_log')
        if os.path.exists(undo_log):
            try:
                with open(undo_log, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception as e:
                self.logger.warning(f" 读取撤销日志失败: {e}")
        history.append(entry)
        try:
            with open(undo_log, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f" 保存撤销日志失败: {e}")

    def _generate_tree_view(self, root_path: str, max_depth: int = 3) -> str:
        if not os.path.exists(root_path):
            return f"{Fore.RED}目录不存在: {root_path}"
        root_node = Node(os.path.basename(root_path), path=root_path)
        def walk(node, path, depth):
            if depth >= max_depth:
                return
            try:
                for item in sorted(os.listdir(path)):
                    full_path = os.path.join(path, item)
                    if self._should_skip_dir(full_path):
                        continue
                    if os.path.isdir(full_path):
                        child = Node(
                            f"{Fore.BLUE}{item}{Style.RESET_ALL}" if depth == 0 else f"{Fore.BLUE}{item}{Style.RESET_ALL}",
                            parent=node, path=full_path
                        )
                        walk(child, full_path, depth+1)
                    elif os.path.isfile(full_path) and self._is_valid_video(full_path):
                        Node(f"{Fore.GREEN}{item}{Style.RESET_ALL}", parent=node)
            except Exception as e:
                Node(f"{Fore.RED}访问错误: {e}{Style.RESET_ALL}", parent=node)
        walk(root_node, root_path, 0)
        return "\n".join([f"{pre}{n.name}" for pre,_,n in RenderTree(root_node)])

    def _should_skip_dir(self, path: str) -> bool:
        if any(excl in path for excl in self.config['rules']['exclude_dirs']):
            return True
        if 'sample' in path.lower() or 'temp' in path.lower():
            return True
        return False

    def _is_valid_video(self, path: str) -> bool:
        return any(path.lower().endswith(ext) for ext in self.config['rules']['extensions'])

    def _backup_file(self, src: str) -> bool:
        try:
            backup_dir = self.config['paths']['backup']
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup_path = os.path.join(backup_dir, f"{os.path.basename(src)}.{timestamp}.bak")
            shutil.copy2(src, backup_path)
            return True
        except Exception as e:
            self.logger.error(f"备份失败: {src} - {e}")
            return False

    def _load_checkpoint(self) -> Set[str]:
        try:
            if os.path.exists(self.config['paths']['checkpoint']):
                with open(self.config['paths']['checkpoint'], 'r') as f:
                    return set(json.load(f))
        except Exception as e:
            self.logger.warning(f"加载检查点失败: {e}")
        return set()

    def _save_checkpoint(self, processed: Set[str]):
        try:
            with open(self.config['paths']['checkpoint'], 'w') as f:
                json.dump(list(processed), f)
        except Exception as e:
            self.logger.error(f"保存检查点失败: {e}")

    def _show_results(self, preview: bool):
        print(f"\n{Fore.CYAN}处理结果汇总:")
        print(f"{'已处理文件':<15}: {self.counters['processed']}")
        print(f"{'成功移动':<15}: {self.counters['moved']}")
        print(f"{'备份文件':<15}: {self.counters['backups']}")
        print(f"{'元数据同步':<15}: {self.counters['meta_moved']}")
        print(f"{'跳过文件':<15}: {self.counters['skipped']}")
        print(f"{'发生错误':<15}: {self.counters['errors']}")

    def edit_config(self):
        print(f"\n{Fore.CYAN}配置编辑模式:")
        print(f"当前配置路径: {self.config_path}")
        print("请手动编辑配置文件或扩展此方法以实现交互式编辑。")

    def undo_operations(self, steps: int):
        print(f"{Fore.YELLOW}撤销功能尚未实现，可自行扩展undo_log的逆操作逻辑。")

# ========================= 主程序 =========================
def main():
    parser = argparse.ArgumentParser(description='电视剧文件整理工具专业版 V2.7')
    parser.add_argument('--preview', action='store_true', help='预览模式')
    parser.add_argument('--execute', action='store_true', help='执行模式')
    parser.add_argument('--incremental', action='store_true', help='启用增量处理')
    parser.add_argument('--undo', type=int, help='撤销操作')
    parser.add_argument('--edit', action='store_true', help='编辑配置')
    parser.add_argument('--config', help='指定配置文件路径')
    args = parser.parse_args()

    processor = TVShowProcessor(args.config)

    if args.incremental:
        processor.config['rules']['incremental_processing'] = True

    try:
        if args.execute:
            processor.process(preview=False)
        elif args.preview:
            processor.process(preview=True)
        elif args.undo:
            processor.undo_operations(args.undo)
        elif args.edit:
            processor.edit_config()
    except Exception as e:
        print(f"{Fore.RED}处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
