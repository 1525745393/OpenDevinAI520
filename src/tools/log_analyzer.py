#!/usr/bin/env python3
"""
日志分析工具
智能分析应用日志，提取关键信息和统计数据
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import gzip
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree

console = Console()


class LogAnalyzer:
    """日志分析工具"""
    
    # 常见日志级别
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'FATAL', 'CRITICAL']
    
    # 常见日志格式模式
    LOG_PATTERNS = {
        'apache_common': r'(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-)',
        'apache_combined': r'(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"',
        'nginx': r'(\S+) - - \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+) "([^"]*)" "([^"]*)"',
        'python_logging': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.+)',
        'syslog': r'(\w{3} \d{1,2} \d{2}:\d{2}:\d{2}) (\S+) (\S+): (.+)',
        'json': r'^\{.*\}$',
        'custom_timestamp': r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})?)',
    }
    
    # HTTP状态码分类
    HTTP_STATUS_CATEGORIES = {
        '2xx': 'Success',
        '3xx': 'Redirection', 
        '4xx': 'Client Error',
        '5xx': 'Server Error'
    }
    
    def __init__(self):
        self.analyzed_files = []
        self.errors = []
        self.operations_log = []
        self.statistics = defaultdict(int)
        self.log_entries = []
        self.patterns_found = {}
    
    def detect_log_format(self, sample_lines: List[str]) -> str:
        """检测日志格式"""
        format_scores = defaultdict(int)
        
        for line in sample_lines[:100]:  # 检查前100行
            line = line.strip()
            if not line:
                continue
                
            for format_name, pattern in self.LOG_PATTERNS.items():
                try:
                    if re.search(pattern, line):
                        format_scores[format_name] += 1
                except re.error:
                    continue
        
        if format_scores:
            best_format = max(format_scores.items(), key=lambda x: x[1])
            return best_format[0]
        
        return 'unknown'
    
    def parse_log_line(self, line: str, log_format: str) -> Optional[Dict]:
        """解析单行日志"""
        line = line.strip()
        if not line:
            return None
        
        try:
            if log_format == 'json':
                return json.loads(line)
            
            pattern = self.LOG_PATTERNS.get(log_format)
            if not pattern:
                return {'raw': line, 'format': 'unknown'}
            
            match = re.search(pattern, line)
            if not match:
                return {'raw': line, 'format': log_format, 'parsed': False}
            
            groups = match.groups()
            
            if log_format in ['apache_common', 'apache_combined', 'nginx']:
                result = {
                    'ip': groups[0],
                    'timestamp': groups[1],
                    'method': groups[2],
                    'url': groups[3],
                    'protocol': groups[4],
                    'status': int(groups[5]),
                    'size': groups[6] if groups[6] != '-' else 0,
                    'format': log_format,
                    'parsed': True
                }
                
                if log_format in ['apache_combined', 'nginx'] and len(groups) >= 9:
                    result['referer'] = groups[7]
                    result['user_agent'] = groups[8]
                
                return result
            
            elif log_format == 'python_logging':
                return {
                    'timestamp': groups[0],
                    'level': groups[1],
                    'logger': groups[2],
                    'message': groups[3],
                    'format': log_format,
                    'parsed': True
                }
            
            elif log_format == 'syslog':
                return {
                    'timestamp': groups[0],
                    'host': groups[1],
                    'process': groups[2],
                    'message': groups[3],
                    'format': log_format,
                    'parsed': True
                }
            
            else:
                return {'raw': line, 'format': log_format, 'parsed': False}
                
        except Exception as e:
            return {'raw': line, 'error': str(e), 'parsed': False}
    
    def extract_timestamps(self, log_entry: Dict) -> Optional[datetime]:
        """提取时间戳"""
        if 'timestamp' not in log_entry:
            return None
        
        timestamp_str = log_entry['timestamp']
        
        # 常见时间格式
        time_formats = [
            '%Y-%m-%d %H:%M:%S,%f',  # Python logging
            '%Y-%m-%d %H:%M:%S.%f',  # ISO with microseconds
            '%Y-%m-%d %H:%M:%S',     # ISO basic
            '%Y-%m-%dT%H:%M:%S.%fZ', # ISO with Z
            '%Y-%m-%dT%H:%M:%SZ',    # ISO with Z no microseconds
            '%d/%b/%Y:%H:%M:%S %z',  # Apache format
            '%b %d %H:%M:%S',        # Syslog format
        ]
        
        for fmt in time_formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # 尝试自动解析
        try:
            from dateutil import parser
            dt = parser.parse(timestamp_str)
            # 如果没有时区信息，假设为本地时区
            if dt.tzinfo is None:
                import pytz
                dt = dt.replace(tzinfo=pytz.UTC)
            return dt
        except:
            return None
    
    def analyze_log_file(self, file_path: str, max_lines: int = None) -> Dict:
        """分析单个日志文件"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 检查是否是压缩文件
            if file_path.suffix == '.gz':
                open_func = gzip.open
                mode = 'rt'
            else:
                open_func = open
                mode = 'r'
            
            console.print(f"📊 分析日志文件: {file_path.name}")
            
            lines = []
            line_count = 0
            
            # 读取文件内容
            with open_func(file_path, mode, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    lines.append(line)
                    line_count += 1
                    if max_lines and line_count >= max_lines:
                        break
            
            if not lines:
                return {'error': '文件为空或无法读取'}
            
            # 检测日志格式
            log_format = self.detect_log_format(lines)
            console.print(f"🔍 检测到日志格式: {log_format}")
            
            # 解析日志条目
            parsed_entries = []
            error_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("解析日志条目", total=len(lines))
                
                for line in lines:
                    progress.update(task, description=f"已处理: {len(parsed_entries)} 条")
                    
                    entry = self.parse_log_line(line, log_format)
                    if entry:
                        if entry.get('parsed', False):
                            parsed_entries.append(entry)
                        else:
                            error_count += 1
                    
                    progress.advance(task)
            
            # 统计分析
            analysis_result = self._analyze_entries(parsed_entries, log_format)
            analysis_result.update({
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'total_lines': line_count,
                'parsed_lines': len(parsed_entries),
                'error_lines': error_count,
                'log_format': log_format,
                'parse_success_rate': f"{(len(parsed_entries) / line_count * 100):.1f}%" if line_count > 0 else "0%"
            })
            
            self.analyzed_files.append(analysis_result)
            self.operations_log.append(f"分析完成: {file_path.name} ({len(parsed_entries)} 条记录)")
            
            return analysis_result
            
        except Exception as e:
            error_msg = f"分析文件 {file_path} 时出错: {str(e)}"
            self.errors.append(error_msg)
            return {'error': error_msg}
    
    def _analyze_entries(self, entries: List[Dict], log_format: str) -> Dict:
        """分析日志条目"""
        if not entries:
            return {'entries': []}
        
        analysis = {
            'entries': entries,
            'total_entries': len(entries),
            'time_range': {},
            'statistics': {},
            'patterns': {},
            'anomalies': []
        }
        
        # 时间分析
        timestamps = []
        for entry in entries:
            ts = self.extract_timestamps(entry)
            if ts:
                timestamps.append(ts)
        
        if timestamps:
            timestamps.sort()
            analysis['time_range'] = {
                'start': timestamps[0].isoformat(),
                'end': timestamps[-1].isoformat(),
                'duration': str(timestamps[-1] - timestamps[0]),
                'total_timestamps': len(timestamps)
            }
        
        # 根据日志格式进行特定分析
        if log_format in ['apache_common', 'apache_combined', 'nginx']:
            analysis['statistics'].update(self._analyze_web_logs(entries))
        elif log_format == 'python_logging':
            analysis['statistics'].update(self._analyze_python_logs(entries))
        elif log_format == 'syslog':
            analysis['statistics'].update(self._analyze_syslog(entries))
        
        # 通用模式分析
        analysis['patterns'] = self._find_patterns(entries)
        
        # 异常检测
        analysis['anomalies'] = self._detect_anomalies(entries, timestamps)
        
        return analysis
    
    def _analyze_web_logs(self, entries: List[Dict]) -> Dict:
        """分析Web服务器日志"""
        stats = {
            'status_codes': Counter(),
            'methods': Counter(),
            'ips': Counter(),
            'urls': Counter(),
            'user_agents': Counter(),
            'total_bytes': 0,
            'unique_ips': set(),
            'error_rate': 0
        }
        
        for entry in entries:
            if 'status' in entry:
                stats['status_codes'][entry['status']] += 1
            if 'method' in entry:
                stats['methods'][entry['method']] += 1
            if 'ip' in entry:
                stats['ips'][entry['ip']] += 1
                stats['unique_ips'].add(entry['ip'])
            if 'url' in entry:
                stats['urls'][entry['url']] += 1
            if 'user_agent' in entry:
                stats['user_agents'][entry['user_agent']] += 1
            if 'size' in entry and isinstance(entry['size'], int):
                stats['total_bytes'] += entry['size']
        
        # 计算错误率
        total_requests = len(entries)
        error_requests = sum(count for status, count in stats['status_codes'].items() 
                           if status >= 400)
        stats['error_rate'] = f"{(error_requests / total_requests * 100):.2f}%" if total_requests > 0 else "0%"
        
        # 转换集合为数量
        stats['unique_ips'] = len(stats['unique_ips'])
        
        return stats
    
    def _analyze_python_logs(self, entries: List[Dict]) -> Dict:
        """分析Python应用日志"""
        stats = {
            'log_levels': Counter(),
            'loggers': Counter(),
            'messages': Counter(),
            'error_messages': [],
            'warning_messages': []
        }
        
        for entry in entries:
            if 'level' in entry:
                stats['log_levels'][entry['level']] += 1
            if 'logger' in entry:
                stats['loggers'][entry['logger']] += 1
            if 'message' in entry:
                message = entry['message']
                stats['messages'][message] += 1
                
                # 收集错误和警告消息
                level = entry.get('level', '').upper()
                if level in ['ERROR', 'CRITICAL', 'FATAL']:
                    stats['error_messages'].append(message)
                elif level in ['WARNING', 'WARN']:
                    stats['warning_messages'].append(message)
        
        return stats
    
    def _analyze_syslog(self, entries: List[Dict]) -> Dict:
        """分析系统日志"""
        stats = {
            'hosts': Counter(),
            'processes': Counter(),
            'messages': Counter(),
            'message_patterns': Counter()
        }
        
        for entry in entries:
            if 'host' in entry:
                stats['hosts'][entry['host']] += 1
            if 'process' in entry:
                stats['processes'][entry['process']] += 1
            if 'message' in entry:
                message = entry['message']
                stats['messages'][message] += 1
                
                # 提取消息模式
                pattern = re.sub(r'\d+', 'N', message)  # 替换数字
                pattern = re.sub(r'\b\w{32,}\b', 'HASH', pattern)  # 替换长字符串
                stats['message_patterns'][pattern] += 1
        
        return stats
    
    def _find_patterns(self, entries: List[Dict]) -> Dict:
        """查找日志模式"""
        patterns = {
            'repeated_messages': Counter(),
            'ip_patterns': Counter(),
            'time_patterns': Counter()
        }
        
        # 查找重复消息
        for entry in entries:
            if 'message' in entry:
                patterns['repeated_messages'][entry['message']] += 1
            elif 'url' in entry:
                patterns['repeated_messages'][entry['url']] += 1
        
        # 只保留出现多次的模式
        patterns['repeated_messages'] = {
            msg: count for msg, count in patterns['repeated_messages'].items() 
            if count > 1
        }
        
        return patterns
    
    def _detect_anomalies(self, entries: List[Dict], timestamps: List[datetime]) -> List[Dict]:
        """检测异常"""
        anomalies = []
        
        if not timestamps:
            return anomalies
        
        # 检测时间间隔异常
        if len(timestamps) > 1:
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                for i, interval in enumerate(intervals):
                    if interval > avg_interval * 10:  # 间隔超过平均值10倍
                        anomalies.append({
                            'type': 'time_gap',
                            'description': f'时间间隔异常: {interval:.2f}秒',
                            'timestamp': timestamps[i+1].isoformat(),
                            'severity': 'medium'
                        })
        
        # 检测状态码异常（针对Web日志）
        status_codes = [entry.get('status') for entry in entries if 'status' in entry]
        if status_codes:
            error_codes = [code for code in status_codes if code >= 500]
            if len(error_codes) > len(status_codes) * 0.1:  # 错误率超过10%
                anomalies.append({
                    'type': 'high_error_rate',
                    'description': f'高错误率: {len(error_codes)}/{len(status_codes)} ({len(error_codes)/len(status_codes)*100:.1f}%)',
                    'severity': 'high'
                })
        
        return anomalies
    
    def batch_analyze(self, directory: str, pattern: str = "*.log", 
                     max_files: int = None, max_lines_per_file: int = None) -> Dict:
        """批量分析日志文件"""
        directory_path = Path(directory)
        if not directory_path.exists():
            error_msg = f"目录不存在: {directory}"
            self.errors.append(error_msg)
            return {'analyzed': [], 'errors': [error_msg]}
        
        # 查找日志文件
        log_files = list(directory_path.glob(pattern))
        if pattern != "*.log":
            # 也查找压缩文件
            log_files.extend(directory_path.glob(pattern + ".gz"))
        
        if not log_files:
            error_msg = f"在目录 {directory} 中未找到匹配 {pattern} 的日志文件"
            self.errors.append(error_msg)
            return {'analyzed': [], 'errors': [error_msg]}
        
        if max_files:
            log_files = log_files[:max_files]
        
        console.print(f"📁 找到 {len(log_files)} 个日志文件")
        
        analyzed_results = []
        errors = []
        
        for file_path in log_files:
            try:
                result = self.analyze_log_file(str(file_path), max_lines_per_file)
                if 'error' in result:
                    errors.append(result['error'])
                else:
                    analyzed_results.append(result)
            except Exception as e:
                error_msg = f"处理文件 {file_path.name} 时出错: {str(e)}"
                errors.append(error_msg)
                self.errors.append(error_msg)
        
        return {
            'analyzed': analyzed_results,
            'errors': errors,
            'total_files': len(log_files),
            'success_count': len(analyzed_results),
            'error_count': len(errors)
        }
    
    def generate_report(self, output_file: str = None) -> Dict:
        """生成分析报告"""
        if not self.analyzed_files:
            return {'error': '没有分析结果可生成报告'}
        
        report = {
            'summary': {
                'total_files': len(self.analyzed_files),
                'total_entries': sum(f.get('total_entries', 0) for f in self.analyzed_files),
                'total_errors': len(self.errors),
                'analysis_time': datetime.now().isoformat()
            },
            'files': self.analyzed_files,
            'global_statistics': self._generate_global_stats(),
            'recommendations': self._generate_recommendations()
        }
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                console.print(f"📄 报告已保存到: {output_file}")
            except Exception as e:
                self.errors.append(f"保存报告失败: {str(e)}")
        
        return report
    
    def _generate_global_stats(self) -> Dict:
        """生成全局统计"""
        global_stats = {
            'total_log_entries': 0,
            'log_formats': Counter(),
            'time_range': {},
            'common_patterns': Counter()
        }
        
        all_timestamps = []
        
        for file_result in self.analyzed_files:
            global_stats['total_log_entries'] += file_result.get('total_entries', 0)
            global_stats['log_formats'][file_result.get('log_format', 'unknown')] += 1
            
            # 收集时间范围
            time_range = file_result.get('time_range', {})
            if time_range.get('start'):
                try:
                    start_time = datetime.fromisoformat(time_range['start'])
                    end_time = datetime.fromisoformat(time_range['end'])
                    all_timestamps.extend([start_time, end_time])
                except:
                    pass
        
        if all_timestamps:
            # 确保所有时间戳都有时区信息
            normalized_timestamps = []
            for ts in all_timestamps:
                if ts.tzinfo is None:
                    import pytz
                    ts = ts.replace(tzinfo=pytz.UTC)
                normalized_timestamps.append(ts)
            
            normalized_timestamps.sort()
            global_stats['time_range'] = {
                'start': normalized_timestamps[0].isoformat(),
                'end': normalized_timestamps[-1].isoformat(),
                'total_duration': str(normalized_timestamps[-1] - normalized_timestamps[0])
            }
        
        return global_stats
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于分析结果生成建议
        for file_result in self.analyzed_files:
            stats = file_result.get('statistics', {})
            
            # Web日志建议
            if 'error_rate' in stats:
                error_rate = float(stats['error_rate'].rstrip('%'))
                if error_rate > 5:
                    recommendations.append(f"高错误率警告: {stats['error_rate']} - 建议检查应用程序错误")
            
            # 异常检测建议
            anomalies = file_result.get('anomalies', [])
            if anomalies:
                high_severity = [a for a in anomalies if a.get('severity') == 'high']
                if high_severity:
                    recommendations.append("检测到高严重性异常，建议立即调查")
        
        if not recommendations:
            recommendations.append("日志分析正常，未发现明显问题")
        
        return recommendations
    
    def display_summary(self):
        """显示分析摘要"""
        if not self.analyzed_files:
            console.print("❌ 没有分析结果")
            return
        
        # 创建摘要表格
        table = Table(title="📊 日志分析摘要")
        table.add_column("文件", style="cyan")
        table.add_column("格式", style="magenta")
        table.add_column("条目数", style="green")
        table.add_column("解析率", style="yellow")
        table.add_column("状态", style="blue")
        
        for result in self.analyzed_files:
            status = "✅ 成功" if 'error' not in result else "❌ 失败"
            table.add_row(
                Path(result.get('file_path', '')).name,
                result.get('log_format', 'unknown'),
                str(result.get('total_entries', 0)),
                result.get('parse_success_rate', '0%'),
                status
            )
        
        console.print(table)
        
        # 显示全局统计
        global_stats = self._generate_global_stats()
        console.print(f"\n📈 总计: {global_stats['total_log_entries']} 条日志记录")
        console.print(f"🕒 时间范围: {global_stats.get('time_range', {}).get('total_duration', 'N/A')}")
        
        # 显示建议
        recommendations = self._generate_recommendations()
        if recommendations:
            console.print("\n💡 建议:")
            for rec in recommendations:
                console.print(f"  • {rec}")
    
    def get_report(self) -> Dict:
        """获取分析报告"""
        return {
            'analyzed_files': self.analyzed_files,
            'errors': self.errors,
            'operations_log': self.operations_log,
            'total_analyzed': len(self.analyzed_files),
            'total_errors': len(self.errors)
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="日志分析工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 分析单个文件
    analyze_parser = subparsers.add_parser('analyze', help='分析单个日志文件')
    analyze_parser.add_argument('file_path', help='日志文件路径')
    analyze_parser.add_argument('--max-lines', type=int, help='最大分析行数')
    analyze_parser.add_argument('--output', help='输出报告文件')
    
    # 批量分析
    batch_parser = subparsers.add_parser('batch', help='批量分析日志文件')
    batch_parser.add_argument('directory', help='日志文件目录')
    batch_parser.add_argument('--pattern', default='*.log', help='文件匹配模式')
    batch_parser.add_argument('--max-files', type=int, help='最大文件数')
    batch_parser.add_argument('--max-lines', type=int, help='每个文件最大分析行数')
    batch_parser.add_argument('--output', help='输出报告文件')
    
    # 实时监控
    monitor_parser = subparsers.add_parser('monitor', help='实时监控日志文件')
    monitor_parser.add_argument('file_path', help='日志文件路径')
    monitor_parser.add_argument('--tail', type=int, default=10, help='显示最后N行')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    analyzer = LogAnalyzer()
    
    try:
        if args.command == 'analyze':
            console.print(f"📊 分析日志文件: {args.file_path}")
            result = analyzer.analyze_log_file(args.file_path, args.max_lines)
            
            if 'error' in result:
                console.print(f"❌ 分析失败: {result['error']}")
            else:
                analyzer.display_summary()
                
                if args.output:
                    analyzer.generate_report(args.output)
        
        elif args.command == 'batch':
            console.print(f"📁 批量分析: {args.directory}")
            result = analyzer.batch_analyze(
                args.directory, 
                args.pattern, 
                args.max_files, 
                args.max_lines
            )
            
            console.print(f"✅ 分析完成: {result['success_count']}/{result['total_files']} 个文件")
            
            if result['errors']:
                console.print(f"❌ 错误: {len(result['errors'])} 个")
                for error in result['errors'][:5]:  # 显示前5个错误
                    console.print(f"  • {error}")
            
            analyzer.display_summary()
            
            if args.output:
                analyzer.generate_report(args.output)
        
        elif args.command == 'monitor':
            console.print(f"👁️ 监控日志文件: {args.file_path}")
            console.print("按 Ctrl+C 停止监控")
            
            # 简单的tail实现
            file_path = Path(args.file_path)
            if not file_path.exists():
                console.print(f"❌ 文件不存在: {args.file_path}")
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # 跳到文件末尾
                    f.seek(0, 2)
                    
                    while True:
                        line = f.readline()
                        if line:
                            # 简单解析并显示
                            entry = analyzer.parse_log_line(line, 'unknown')
                            if entry and entry.get('parsed'):
                                console.print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.strip()}")
                            else:
                                console.print(f"[{datetime.now().strftime('%H:%M:%S')}] {line.strip()}")
                        else:
                            import time
                            time.sleep(0.1)
            except KeyboardInterrupt:
                console.print("\n👋 监控已停止")
        
    except KeyboardInterrupt:
        console.print("\n⚠️ 操作被用户取消")
    except Exception as e:
        console.print(f"\n❌ 执行失败: {str(e)}")


if __name__ == "__main__":
    main()