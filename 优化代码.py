#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电视剧文件整理工具专业版 V2.6+V2.7 融合优化版

功能亮点：
- 自动生成 YAML 配置，正则全部用单引号，兼容 YAML
- 支持并发/断点续传/撤销/热重载/详细进度报告
- 交互/参数双模式，丰富错误处理与目录树展示
- 适配少量定制（如 metadata_extensions 支持图片）
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
import functools
from typing import Optional, Dict, List, Any, Tuple, Set, Callable
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init as colorama_init
from tqdm import tqdm
from anytree import Node, RenderTree
from concurrent.futures import ThreadPoolExecutor, as_completed

colorama_init(autoreset=True)

class ConfigManager:
    DEFAULT_CONFIG = '''version: "2.6"
paths:
  tv_shows: '/volume1/电视剧待整理'
  backup: '/volume1/电视剧待整理/备份'
  output: '/volume1/电视剧整理完成'
  undo_log: 'undo_log.json'
  log_dir: 'logs'
  checkpoint: 'checkpoint.json'

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
  retry_on_error: true
  parallel_processing: true
  max_workers: 4

patterns:
  title_season:
    - pattern: '^(.+?)(?:\.\d{4})?\.(S\d+)'
      description: '标准季数格式: S01'
    - pattern: '^(.+?)\s+(?:Season|Saison)\s*(\d+)'
      description: 'Season 1'
    - pattern: '^(.+?)\s+第(\d+)季'
      description: '第1季'
    - pattern: '^(.+?)[\s\.]*(?:第)?([一二三四五六七八九十]+)[季部]'
      description: '第一季'
    - pattern: '^(.+?)[\s\.-]+(\d{1,2})[季部]'
      description: '1季'
  episode:
    - pattern: 'E(\d{1,3})'
      description: 'E01'
    - pattern: 'EP(\d{1,3})'
      description: 'EP01'
    - pattern: '\[第?(\d{1,3})[集话]\]'
      description: '[01]'
    - pattern: '\s(\d{1,3})\.'
      description: '01.'
    - pattern: '第([一二三四五六七八九十百]+)[集话]'
      description: '第一集'
    - pattern: '-\s*(\d{1,3})[\s\.]'
      description: '-01'
    - pattern: '集(\d{1,3})'
      description: '集01'
  dir_season:
    - pattern: '[Ss](\d+)'
      description: 'S01'
    - pattern: 'Season[\s\.]*?(\d+)'
      description: 'Season 1'
    - pattern: '第([一二三四五六七八九十]+)季'
      description: '第一季'
    - pattern: 'Season\s*([一二三四五六七八九十]+)'
      description: '第一季'

naming:
  pattern: '{title}.S{season:02d}.E{episode:02d}{ext}'
  dir_pattern: '{title}/Season {season:02d}'
  season_as_dir: true
'''

    _config_cache = {}
    _config_mtimes = {}

    @classmethod
    def initialize_config(cls, config_path: str) -> bool:
        try:
            config_dir = os.path.dirname(config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(cls.DEFAULT_CONFIG)
            return True
        except Exception as e:
            print(f"{Fore.RED}无法创建配置文件: {e}")
            return False

    @classmethod
    def load_config(cls, config_path: str = None) -> Dict:
        if not config_path:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, 'config.yaml')

        if not os.path.exists(config_path):
            print(f"{Fore.YELLOW}未找到配置文件，尝试创建默认配置...")
            if cls.initialize_config(config_path):
                print(f"{Fore.GREEN}默认配置文件已创建于: {config_path}")
                print(f"{Fore.CYAN}请修改以下关键路径后重新运行:")
                print(f" tv_shows: 待整理的电视剧目录")
                print(f" output: 整理后的输出目录")
                sys.exit(0)
            else:
                print(f"{Fore.YELLOW}将使用内存中的默认配置")
                config = yaml.safe_load(cls.DEFAULT_CONFIG)
                cls._config_cache[config_path] = config
                return config

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            cls._config_cache[config_path] = config
            cls._config_mtimes[config_path] = os.path.getmtime(config_path)
            return config
        except Exception as e:
            print(f"{Fore.RED}配置文件加载失败: {e}")
            print(f"{Fore.YELLOW}将使用内存中的默认配置")
            config = yaml.safe_load(cls.DEFAULT_CONFIG)
            cls._config_cache[config_path] = config
            return config

    @classmethod
    def edit_config_interactively(cls, config_path: str):
        if not os.path.exists(config_path):
            print(f"{Fore.RED}配置文件不存在: {config_path}")
            return
        editor = os.getenv('EDITOR', 'nano')
        try:
            os.system(f"{editor} {config_path}")
            print(f"{Fore.GREEN}配置编辑完成")
        except Exception as e:
            print(f"{Fore.RED}编辑配置失败: {e}")

def memoize(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

@memoize
def compile_regex(pattern, flags=0):
    return re.compile(pattern, flags)

class TVShowProcessor:
    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.config = ConfigManager.load_config(config_path)
        self.last_reload = datetime.now()
        self.counters = {
            'processed': 0,
            'moved': 0,
            'skipped': 0,
            'errors': 0,
            'backups': 0,
            'parallel_success': 0,
            'parallel_errors': 0
        }
        self._init_components()
        self._verify_paths()
        self._ensure_required_files()
        self.start_time = time.time()

    def _ensure_required_files(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = self.config['paths'].get('log_dir', 'logs')
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(script_dir, log_dir)
        os.makedirs(log_dir, exist_ok=True)
        undo_log = self.config['paths'].get('undo_log', 'undo_log.json')
        if not os.path.isabs(undo_log):
            undo_log = os.path.join(script_dir, undo_log)
        if not os.path.exists(undo_log):
            with open(undo_log, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        checkpoint = self.config['paths'].get('checkpoint', 'checkpoint.json')
        if not os.path.isabs(checkpoint):
            checkpoint = os.path.join(script_dir, checkpoint)
        if not os.path.exists(checkpoint):
            with open(checkpoint, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _init_components(self):
        self._init_logger()
        self._init_matchers()
        self.last_config_mtime = os.path.getmtime(self.config_path) if self.config_path else 0
        self.history_file = self.config['paths'].get('undo_log', '')
        self.checkpoint_file = self.config['paths'].get('checkpoint', '')
        self._dir_tree_cache = {}

    def _verify_paths(self):
        required_paths = ['tv_shows', 'output']
        for path_key in required_paths:
            path = self.config['paths'].get(path_key, '')
            if not path:
                raise ValueError(f"必须配置路径: {path_key}")
            if not os.path.exists(path):
                print(f"{Fore.YELLOW}警告: 路径不存在 - {path_key}: {path}")

    def _init_logger(self):
        log_dir = self.config['paths'].get('log_dir', 'logs')
        try:
            if not os.path.isabs(log_dir):
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), log_dir)
            os.makedirs(log_dir, exist_ok=True)
        except OSError as e:
            raise ValueError(f"无法创建日志目录: {log_dir} - {e}")

        self.logger = logging.getLogger('TVShowPro')
        self.logger.setLevel(logging.INFO)
        fmt_text = '%(asctime)s [%(levelname)s] %(message)s'
        fmt_json = '{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
        date_fmt = '%Y-%m-%d %H:%M:%S'

        log_file = os.path.join(log_dir, f"process_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(fmt_text, date_fmt))

        json_log_file = os.path.join(log_dir, f"process_{datetime.now().strftime('%Y%m%d')}.json.log")
        json_handler = RotatingFileHandler(
            json_log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        json_handler.setFormatter(logging.Formatter(fmt_json, date_fmt))

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(fmt_text, date_fmt))

        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        self.logger.addHandler(json_handler)
        self.logger.addHandler(console_handler)
        self.logger.info("="*50)
        self.logger.info(" 电视剧整理工具启动")
        self.logger.info(f" 配置文件: {self.config_path or '默认配置'}")

    def _init_matchers(self):
        self.episode_patterns = [
            (compile_regex(p['pattern'], re.IGNORECASE), p['description'])
            for p in self.config['patterns']['episode']
        ]
        self.title_season_patterns = [
            (compile_regex(p['pattern']), p['description'])
            for p in self.config['patterns']['title_season']
        ]
        self.dir_season_patterns = [
            (compile_regex(p['pattern']), p['description'])
            for p in self.config['patterns']['dir_season']
        ]

    def process(self, preview: Optional[bool] = None):
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
        if not all_files:
            print(f"{Fore.YELLOW}没有找到需要处理的文件")
            return
        if self.config['rules'].get('parallel_processing', False) and not preview:
            self._process_files_parallel(all_files, preview, processed)
        else:
            self._process_files_sequential(all_files, preview, processed)
        self._show_results(preview)

    def _process_files_sequential(self, all_files: List[str], preview: bool, processed: Set[str]):
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

    def _process_files_parallel(self, all_files: List[str], preview: bool, processed: Set[str]):
        max_workers = self.config['rules'].get('max_workers', 4)
        self.logger.info(f" 并行处理: 使用 {max_workers} 个工作线程")
        initial_errors = self.counters['errors']
        def process_file(filepath):
            try:
                self._process_single_file(filepath, preview)
                processed.add(filepath)
                self._save_checkpoint(processed)
                return True
            except Exception as e:
                self.logger.error(f" 处理失败: {filepath} - {e}", exc_info=True)
                return False
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_file, file): file for file in all_files}
            with tqdm(total=len(all_files), desc="并行处理进度", unit="文件",
                      bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                for future in as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        success = future.result()
                        if success:
                            self.counters['parallel_success'] += 1
                        else:
                            self.counters['parallel_errors'] += 1
                    except Exception as e:
                        self.logger.error(f" 处理异常: {file} - {e}", exc_info=True)
                        self.counters['parallel_errors'] += 1
                    finally:
                        pbar.update(1)
        self.counters['errors'] = initial_errors + self.counters['parallel_errors']

    def _collect_files(self, root: str, processed: Set[str]) -> List[str]:
        all_files = []
        for root_dir, _, files in os.walk(root):
            if not self.config['rules']['recursive'] and root_dir != root:
                continue
            if self._should_skip_dir(root_dir):
                continue
            for filename in files:
                filepath = os.path.join(root_dir, filename)
                if (self._is_valid_video(filepath) and
                    filepath not in processed and
                    not self._should_skip(filepath)):
                    all_files.append(filepath)
        return all_files

    def _process_single_file(self, filepath: str, preview: bool):
        self.counters['processed'] += 1
        info = self.extract_info(filepath)
        if not info:
            self.counters['skipped'] += 1
            self.logger.warning(f" 无法解析: {os.path.basename(filepath)}")
            return
        self._move_file(filepath, info, preview)

    def _move_file(self, src: str, info: Dict, preview: bool):
        new_path = self._build_output_path(info)
        base_src = os.path.splitext(src)[0]
        new_base = os.path.splitext(new_path)[0]
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if preview:
            rel_path = os.path.relpath(new_path, self.config['paths']['output'])
            print(f"{Fore.GREEN}预览: {os.path.basename(src)} → {rel_path}")
            self.logger.info(f" 预览移动: {src} → {new_path}")
        else:
            if self._backup_file(src):
                self.counters['backups'] += 1
            try:
                shutil.move(src, new_path)
                self._record_undo_action(src, new_path)
                print(f"{Fore.YELLOW}已移动: {os.path.basename(src)} → {os.path.basename(new_path)}")
                self.logger.info(f" 移动完成: {src} → {new_path}")
                self.counters['moved'] += 1
            except Exception as e:
                if self.config['rules'].get('retry_on_error', False):
                    try:
                        self._process_with_fallback(src, new_path, info)
                        self.counters['moved'] += 1
                    except Exception as fallback_e:
                        raise RuntimeError(f"移动失败: {e}")
                else:
                    raise RuntimeError(f"移动失败: {e}")
            for ext in self.config['rules']['metadata_extensions']:
                old_meta = f"{base_src}{ext}"
                new_meta = f"{new_base}{ext}"
                if os.path.exists(old_meta):
                    if preview:
                        print(f"{Fore.CYAN}预览元数据: {os.path.basename(old_meta)} → {os.path.basename(new_meta)}")
                    else:
                        try:
                            shutil.move(old_meta, new_meta)
                            self._record_undo_action(old_meta, new_meta)
                            self.logger.info(f" 移动元数据: {old_meta} → {new_meta}")
                        except Exception as e:
                            self.logger.error(f" 移动元数据失败: {e}")

    def _process_with_fallback(self, src: str, new_path: str, info: Dict):
        self.logger.info(f" 尝试备用处理路径: {os.path.basename(src)}")
        temp_dir = os.path.join(os.path.dirname(new_path), ".temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, os.path.basename(src))
        shutil.move(src, temp_path)
        shutil.move(temp_path, new_path)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
        self._record_undo_action(src, new_path)
        self.logger.info(f" 备用处理成功: {src} → {new_path}")

    def _backup_file(self, filepath: str) -> bool:
        backup_dir = self.config['paths'].get('backup', '')
        if not backup_dir:
            return False
        try:
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(filepath))
            shutil.copy2(filepath, backup_path)
            self.logger.info(f" 备份成功: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f" 备份失败: {e}")
            return False

    def _show_results(self, preview: bool):
        elapsed_time = time.time() - self.start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        if self.config['rules']['show_tree'] and not preview:
            output_dir = self.config['paths']['output']
            if os.path.exists(output_dir):
                print(f"\n{Fore.CYAN}【处理后目录结构】{output_dir}")
                print(self._generate_tree_view(output_dir))
        stats = (f"\n{Fore.GREEN}处理完成: 耗时 {elapsed_str}\n"
                f" 总处理: {self.counters['processed']}\n"
                f" 成功移动: {self.counters['moved']}\n"
                f" 备份文件: {self.counters['backups']}\n"
                f" 跳过文件: {self.counters['skipped']}\n"
                f" 错误数量: {self.counters['errors']}")
        if self.config['rules'].get('parallel_processing', False) and not preview:
            stats += (f"\n 并行处理成功: {self.counters['parallel_success']}\n"
                     f" 并行处理失败: {self.counters['parallel_errors']}")
        print(stats)
        self.logger.info(stats)

    def _generate_tree_view(self, root_path: str, max_depth: int = 3) -> str:
        cache_key = (root_path, max_depth)
        if cache_key in self._dir_tree_cache:
            return self._dir_tree_cache[cache_key]
        if not os.path.exists(root_path):
            result = f"{Fore.RED}目录不存在: {root_path}"
            self._dir_tree_cache[cache_key] = result
            return result
        root_node = Node(os.path.basename(root_path), path=root_path)
        def walk(node, path, depth):
            if depth >= max_depth:
                return
            try:
                for item in sorted(os.listdir(path)):
                    if self._should_skip_dir(os.path.join(path, item)):
                        continue
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        child = Node(f"{Fore.BLUE}{item}{Style.RESET_ALL}", parent=node, path=full_path)
                        walk(child, full_path, depth+1)
                    elif os.path.isfile(full_path) and self._is_valid_video(full_path):
                        Node(f"{Fore.GREEN}{item}{Style.RESET_ALL}", parent=node)
            except Exception as e:
                Node(f"{Fore.RED}!访问错误: {e}", parent=node)
        walk(root_node, root_path, 0)
        result = "\n".join([f"{pre}{n.name}" for pre,_,n in RenderTree(root_node)])
        self._dir_tree_cache[cache_key] = result
        return result

    def _load_checkpoint(self) -> Set[str]:
        if not self.checkpoint_file or not os.path.exists(self.checkpoint_file):
            return set()
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            self.logger.warning(f" 检查点文件损坏: {e}")
            return set()

    def _save_checkpoint(self, processed: Set[str]):
        if not self.checkpoint_file:
            return
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(list(processed), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f" 保存检查点失败: {e}")

    def _record_undo_action(self, original: str, new_path: str):
        if not self.history_file:
            return
        entry = {
            'timestamp': datetime.now().isoformat(),
            'original': original,
            'new_path': new_path,
            'action': 'move'
        }
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception as e:
                self.logger.warning(f" 历史文件损坏: {e}")
        history.append(entry)
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f" 保存撤销记录失败: {e}")

    def undo_last_actions(self, steps: int = 1):
        if not self.history_file or not os.path.exists(self.history_file):
            print(f"{Fore.RED}无撤销记录")
            return
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception as e:
            print(f"{Fore.RED}历史文件损坏: {e}")
            return
        count = min(steps, len(history))
        success = 0
        for entry in reversed(history[-count:]):
            try:
                if os.path.exists(entry['new_path']):
                    shutil.move(entry['new_path'], entry['original'])
                    print(f"{Fore.GREEN}撤销: {os.path.basename(entry['new_path'])} → {os.path.basename(entry['original'])}")
                    success += 1
                else:
                    print(f"{Fore.YELLOW}文件不存在: {entry['new_path']}")
            except Exception as e:
                print(f"{Fore.RED}撤销失败: {e}")
        remaining = history[:-count] if count < len(history) else []
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(remaining, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"{Fore.RED}保存撤销记录失败: {e}")
        print(f"{Fore.CYAN}撤销完成: {success}/{count} 个操作")

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

    def _should_skip_dir(self, dirpath: str) -> bool:
        dirname = os.path.basename(dirpath).lower()
        exclude_dirs = self.config['rules']['exclude_dirs']
        return any(exclude_dir.lower() in dirname for exclude_dir in exclude_dirs)

    def _should_skip(self, filepath: str) -> bool:
        filename = os.path.basename(filepath).lower()
        exclude_keywords = self.config['rules']['exclude_keywords']
        return any(kw in filename for kw in exclude_keywords)

    def _is_valid_video(self, filepath: str) -> bool:
        try:
            if not os.path.isfile(filepath):
                return False
            ext = os.path.splitext(filepath)[1].lower()
            if ext not in self.config['rules']['extensions']:
                return False
            min_size = self.config['rules']['min_size_mb']
            if min_size > 0:
                file_size = os.path.getsize(filepath) / (1024 ** 2)
                return file_size >= min_size
            return True
        except OSError:
            return False

    def extract_info(self, filepath: str) -> Optional[Dict]:
        filename = os.path.basename(filepath)
        basename, ext = os.path.splitext(filename)
        dirname = os.path.basename(os.path.dirname(filepath))
        parent_dirname = os.path.basename(os.path.dirname(os.path.dirname(filepath)))
        processing_steps = [
            lambda: self._extract_info_from_dir(dirname, parent_dirname),
            lambda: self._extract_info_from_filename(basename),
            lambda: self._extract_mixed_info(dirname, parent_dirname, basename)
        ]
        for step in processing_steps:
            result = step()
            if result:
                result['title'] = self._filter_chinese(result['title'])
                result['ext'] = ext
                return result
        self.logger.warning(f" 无法解析: {filename}")
        return None

    def _extract_mixed_info(self, dirname, parent_dirname, basename):
        season = self._extract_season_from_dir(dirname)
        if season is None:
            season = self._extract_season_from_dir(parent_dirname)
        if season is not None:
            title = self._extract_title_from_filename(basename)
            if title:
                episode = self._extract_episode(basename)
                if episode is not None:
                    return {
                        'title': title,
                        'season': season,
                        'episode': episode
                    }
        return None

    def _extract_info_from_dir(self, dirname: str, parent_dirname: str) -> Optional[Dict]:
        for pattern, _ in self.dir_season_patterns:
            match = pattern.search(dirname)
            if match:
                season = self._parse_season_number(match.group(1))
                if season is not None:
                    title = re.sub(pattern.pattern, '', dirname).strip()
                    if title:
                        episode = 1
                        return {
                            'title': title,
                            'season': season,
                            'episode': episode
                        }
        for pattern, _ in self.dir_season_patterns:
            match = pattern.search(parent_dirname)
            if match:
                season = self._parse_season_number(match.group(1))
                if season is not None:
                    return {
                        'title': dirname,
                        'season': season,
                        'episode': 1
                    }
        return None

    def _extract_info_from_filename(self, basename: str) -> Optional[Dict]:
        for pattern, _ in self.title_season_patterns:
            match = pattern.search(basename)
            if match:
                title = match.group(1).replace('.', ' ').strip()
                season = self._parse_season_number(match.group(2))
                if title and season is not None:
                    remaining = basename[match.end():]
                    episode = self._extract_episode(remaining)
                    if episode is not None:
                        return {
                            'title': title,
                            'season': season,
                            'episode': episode
                        }
        return None

    def _extract_title_from_filename(self, basename: str) -> Optional[str]:
        title = re.sub(r'[\._\-]\[.*?\]', '', basename)
        title = re.sub(r'[\._\-]\(.*?\)', '', title)
        title = re.sub(r'[\._\-]HD.*', '', title)
        title = re.sub(r'[\._\-]S\d+.*', '', title)
        title = re.sub(r'[\._\-]E\d+.*', '', title)
        title = re.sub(r'[\._\-]\d{4}.*', '', title)
        title = title.replace('.', ' ').strip()
        if title:
            return title
        return None

    def _extract_season_from_dir(self, dirname: str) -> Optional[int]:
        for pattern, _ in self.dir_season_patterns:
            match = pattern.search(dirname)
            if match:
                return self._parse_season_number(match.group(1))
        return None

    def _extract_episode(self, basename: str) -> Optional[int]:
        for pattern, _ in self.episode_patterns:
            match = pattern.search(basename)
            if match:
                return self._parse_episode_number(match.group(1))
        return None

    def _parse_season_number(self, s: str) -> Optional[int]:
        cn_numbers = {'一':1, '二':2, '三':3, '四':4, '五':5,
                      '六':6, '七':7, '八':8, '九':9, '十':10}
        if s in cn_numbers:
            return cn_numbers[s]
        try:
            return int(s.lstrip('Ss'))
        except ValueError:
            return None

    def _parse_episode_number(self, s: str) -> Optional[int]:
        cn_numbers = {'一':1, '二':2, '三':3, '四':4, '五':5,
                      '六':6, '七':7, '八':8, '九':9, '十':10,
                      '十一':11, '十二':12, '十三':13, '十四':14,
                      '十五':15, '十六':16, '十七':17, '十八':18,
                      '十九':19, '二十':20}
        if s in cn_numbers:
            return cn_numbers[s]
        try:
            return int(s)
        except ValueError:
            return None

    def _filter_chinese(self, text: str) -> str:
        if not text:
            return text
        chinese_text = re.findall(r'[\u4e00-\u9fff]+', text)
        if chinese_text:
            return ' '.join(chinese_text)
        return text

    def edit_config(self):
        if not self.config_path:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(script_dir, 'config.yaml')
        ConfigManager.edit_config_interactively(self.config_path)
        self.config = ConfigManager.load_config(self.config_path)
        self._init_matchers()
        print(f"{Fore.GREEN}配置已重新加载")

def main():
    parser = argparse.ArgumentParser(
        description='电视剧文件整理工具专业版 V2.6+V2.7融合版',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--config', help='指定配置文件路径（可选）')
    parser.add_argument('--preview', action='store_true', help='仅预览不执行')
    parser.add_argument('--execute', action='store_true', help='执行整理操作')
    parser.add_argument('--undo', type=int, metavar='N', help='撤销最近N次操作')
    parser.add_argument('--edit', action='store_true', help='交互式编辑配置')
    parser.add_argument('--interactive', '-i', action='store_true', help='进入交互模式')

    if len(sys.argv) == 1:
        print(f"{Fore.CYAN}\n欢迎使用电视剧文件整理工具 V2.6+V2.7融合版")
        print(f"{Fore.YELLOW}\n首次使用请按照以下步骤操作：")
        print("1. 首次运行会自动生成配置文件")
        print("2. 修改配置文件中的路径设置")
        print("3. 使用预览模式检查效果")
        print("4. 确认无误后执行整理\n")
        print(f"{Fore.GREEN}常用命令示例：")
        print(" python tv_rename.py --preview # 预览模式")
        print(" python tv_rename.py --execute # 执行模式")
        print(" python tv_rename.py --edit # 编辑配置")
        print(" python tv_rename.py --undo 3 # 撤销最近3次操作")
        print(" python tv_rename.py --interactive # 进入交互模式")
        print("\n或直接运行进入交互模式: python tv_rename.py -i")
        sys.exit(1)

    args = parser.parse_args()

    try:
        processor = TVShowProcessor(args.config)
        if args.interactive:
            print(f"{Fore.CYAN}\n进入交互模式...")
            while True:
                print(f"\n{Style.BRIGHT}{Fore.BLUE}=== 媒体整理专家 ===")
                print(f"{Fore.YELLOW}1. 预览")
                print(f"{Fore.YELLOW}2. 执行")
                print(f"{Fore.YELLOW}3. 撤销")
                print(f"{Fore.YELLOW}4. 打开配置")
                print(f"{Fore.YELLOW}5. 退出")
                c = input(f"{Fore.WHITE}选(1-5):").strip()
                if c == '1':
                    processor.process(preview=True)
                elif c == '2':
                    if input(f"{Fore.RED}确认执行？(y/n):").lower() == 'y':
                        processor.process(preview=False)
                elif c == '3':
                    s = input('撤销步数:') or '1'
                    processor.undo_last_actions(int(s) if s.isdigit() else 1)
                elif c == '4':
                    processor.edit_config()
                elif c == '5':
                    break
                else:
                    print(f"{Fore.RED}无效选择")
            return
        elif args.edit:
            processor.edit_config()
        elif args.undo:
            processor.undo_last_actions(args.undo)
        elif args.preview:
            processor.process(preview=True)
        elif args.execute:
            confirm = input(f"{Fore.YELLOW}确定要执行文件整理操作吗？(y/n): ")
            if confirm.lower() == 'y':
                processor.process(preview=False)
            else:
                print(f"{Fore.CYAN}操作已取消")
        else:
            parser.print_help()
    except Exception as e:
        print(f"\n{Fore.RED}错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
