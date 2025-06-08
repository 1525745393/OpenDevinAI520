#!/usr/bin/env python3
"""
数据转换工具
支持多种数据格式之间的转换：JSON, CSV, XML, YAML, Excel等
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path
from typing import Dict, List, Any, Union
import pandas as pd
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


class DataConverter:
    """数据转换工具"""
    
    SUPPORTED_FORMATS = {
        'json': ['.json'],
        'csv': ['.csv'],
        'xml': ['.xml'],
        'yaml': ['.yaml', '.yml'],
        'excel': ['.xlsx', '.xls'],
        'tsv': ['.tsv'],
        'parquet': ['.parquet'],
        'html': ['.html', '.htm']
    }
    
    def __init__(self):
        self.converted_files = []
        self.errors = []
        self.operations_log = []
    
    def detect_format(self, file_path: str) -> str:
        """检测文件格式"""
        extension = Path(file_path).suffix.lower()
        
        for format_name, extensions in self.SUPPORTED_FORMATS.items():
            if extension in extensions:
                return format_name
        
        return 'unknown'
    
    def read_json(self, file_path: str) -> Union[Dict, List]:
        """读取JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def read_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """读取CSV文件"""
        return pd.read_csv(file_path, **kwargs)
    
    def read_xml(self, file_path: str) -> Dict:
        """读取XML文件"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        def xml_to_dict(element):
            result = {}
            
            # 添加属性
            if element.attrib:
                result['@attributes'] = element.attrib
            
            # 添加文本内容
            if element.text and element.text.strip():
                if len(element) == 0:
                    return element.text.strip()
                result['#text'] = element.text.strip()
            
            # 添加子元素
            for child in element:
                child_data = xml_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data
            
            return result
        
        return {root.tag: xml_to_dict(root)}
    
    def read_yaml(self, file_path: str) -> Union[Dict, List]:
        """读取YAML文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def read_excel(self, file_path: str, **kwargs) -> pd.DataFrame:
        """读取Excel文件"""
        return pd.read_excel(file_path, **kwargs)
    
    def read_tsv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """读取TSV文件"""
        return pd.read_csv(file_path, sep='\t', **kwargs)
    
    def read_parquet(self, file_path: str) -> pd.DataFrame:
        """读取Parquet文件"""
        return pd.read_parquet(file_path)
    
    def write_json(self, data: Any, file_path: str, **kwargs):
        """写入JSON文件"""
        # 如果数据是DataFrame，转换为字典
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, **kwargs)
    
    def write_csv(self, data: Any, file_path: str, **kwargs):
        """写入CSV文件"""
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False, **kwargs)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, **kwargs)
        else:
            raise ValueError("数据格式不支持转换为CSV")
    
    def write_xml(self, data: Any, file_path: str, root_name: str = 'root'):
        """写入XML文件"""
        def dict_to_xml(parent, data, item_name='item'):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key.startswith('@'):
                        continue
                    elif key == '#text':
                        parent.text = str(value)
                    else:
                        child = ET.SubElement(parent, key)
                        dict_to_xml(child, value, key)
            elif isinstance(data, list):
                for item in data:
                    child = ET.SubElement(parent, item_name)
                    dict_to_xml(child, item, item_name)
            else:
                parent.text = str(data)
        
        # 如果数据是DataFrame，转换为字典列表
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        root = ET.Element(root_name)
        dict_to_xml(root, data)
        
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def write_yaml(self, data: Any, file_path: str, **kwargs):
        """写入YAML文件"""
        # 如果数据是DataFrame，转换为字典
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, **kwargs)
    
    def write_excel(self, data: Any, file_path: str, **kwargs):
        """写入Excel文件"""
        if isinstance(data, pd.DataFrame):
            data.to_excel(file_path, index=False, **kwargs)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, **kwargs)
        else:
            raise ValueError("数据格式不支持转换为Excel")
    
    def write_tsv(self, data: Any, file_path: str, **kwargs):
        """写入TSV文件"""
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, sep='\t', index=False, **kwargs)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_csv(file_path, sep='\t', index=False, **kwargs)
        else:
            raise ValueError("数据格式不支持转换为TSV")
    
    def write_parquet(self, data: Any, file_path: str, **kwargs):
        """写入Parquet文件"""
        if isinstance(data, pd.DataFrame):
            data.to_parquet(file_path, **kwargs)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_parquet(file_path, **kwargs)
        else:
            raise ValueError("数据格式不支持转换为Parquet")
    
    def write_html(self, data: Any, file_path: str, **kwargs):
        """写入HTML文件"""
        if isinstance(data, pd.DataFrame):
            data.to_html(file_path, index=False, **kwargs)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
            df.to_html(file_path, index=False, **kwargs)
        else:
            raise ValueError("数据格式不支持转换为HTML")
    
    def convert_file(self, input_file: str, output_file: str, **kwargs) -> bool:
        """转换单个文件"""
        try:
            input_format = self.detect_format(input_file)
            output_format = self.detect_format(output_file)
            
            if input_format == 'unknown':
                raise ValueError(f"不支持的输入文件格式: {input_file}")
            
            if output_format == 'unknown':
                raise ValueError(f"不支持的输出文件格式: {output_file}")
            
            # 读取数据
            read_method = getattr(self, f'read_{input_format}')
            data = read_method(input_file, **kwargs.get('read_options', {}))
            
            # 写入数据
            write_method = getattr(self, f'write_{output_format}')
            write_method(data, output_file, **kwargs.get('write_options', {}))
            
            self.converted_files.append({
                'input': input_file,
                'output': output_file,
                'input_format': input_format,
                'output_format': output_format
            })
            
            self.operations_log.append(f"转换: {input_file} -> {output_file}")
            return True
            
        except Exception as e:
            error_msg = f"转换文件 {input_file} 时出错: {str(e)}"
            self.errors.append(error_msg)
            return False
    
    def batch_convert(self, input_dir: str, output_dir: str, 
                     input_format: str, output_format: str, **kwargs) -> Dict:
        """批量转换文件"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        if not input_path.exists():
            error_msg = f"输入目录不存在: {input_dir}"
            self.errors.append(error_msg)
            return {'converted': 0, 'errors': [error_msg]}
        
        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取输入文件
        input_extensions = self.SUPPORTED_FORMATS.get(input_format, [])
        input_files = []
        
        for ext in input_extensions:
            input_files.extend(input_path.glob(f'*{ext}'))
        
        if not input_files:
            error_msg = f"在目录 {input_dir} 中未找到 {input_format} 格式的文件"
            self.errors.append(error_msg)
            return {'converted': 0, 'errors': [error_msg]}
        
        converted_count = 0
        errors = []
        
        # 获取输出扩展名
        output_ext = self.SUPPORTED_FORMATS[output_format][0]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔄 批量转换", total=len(input_files))
            
            for input_file in input_files:
                try:
                    progress.update(task, description=f"转换: {input_file.name}")
                    
                    # 生成输出文件名
                    output_file = output_path / f"{input_file.stem}{output_ext}"
                    
                    if self.convert_file(str(input_file), str(output_file), **kwargs):
                        converted_count += 1
                    else:
                        errors.extend(self.errors[-1:])  # 添加最新的错误
                    
                except Exception as e:
                    error_msg = f"处理文件 {input_file.name} 时出错: {str(e)}"
                    errors.append(error_msg)
                    self.errors.append(error_msg)
                
                progress.advance(task)
        
        return {
            'converted': converted_count,
            'total_files': len(input_files),
            'errors': errors,
            'success_rate': f"{(converted_count / len(input_files) * 100):.1f}%"
        }
    
    def merge_files(self, input_files: List[str], output_file: str, **kwargs) -> bool:
        """合并多个文件"""
        try:
            all_data = []
            
            for input_file in input_files:
                input_format = self.detect_format(input_file)
                if input_format == 'unknown':
                    raise ValueError(f"不支持的文件格式: {input_file}")
                
                read_method = getattr(self, f'read_{input_format}')
                data = read_method(input_file)
                
                # 统一数据格式
                if isinstance(data, pd.DataFrame):
                    all_data.append(data)
                elif isinstance(data, list):
                    all_data.extend(data)
                elif isinstance(data, dict):
                    all_data.append(data)
            
            # 合并数据
            if all(isinstance(d, pd.DataFrame) for d in all_data):
                merged_data = pd.concat(all_data, ignore_index=True)
            else:
                merged_data = all_data
            
            # 写入合并后的文件
            output_format = self.detect_format(output_file)
            write_method = getattr(self, f'write_{output_format}')
            write_method(merged_data, output_file, **kwargs)
            
            self.operations_log.append(f"合并: {len(input_files)} 个文件 -> {output_file}")
            return True
            
        except Exception as e:
            error_msg = f"合并文件时出错: {str(e)}"
            self.errors.append(error_msg)
            return False
    
    def split_file(self, input_file: str, output_dir: str, 
                   split_by: str = 'rows', chunk_size: int = 1000, **kwargs) -> Dict:
        """拆分文件"""
        try:
            input_format = self.detect_format(input_file)
            if input_format == 'unknown':
                raise ValueError(f"不支持的文件格式: {input_file}")
            
            # 读取数据
            read_method = getattr(self, f'read_{input_format}')
            data = read_method(input_file)
            
            if not isinstance(data, pd.DataFrame):
                if isinstance(data, list):
                    data = pd.DataFrame(data)
                else:
                    raise ValueError("数据格式不支持拆分")
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            input_path = Path(input_file)
            base_name = input_path.stem
            extension = input_path.suffix
            
            split_files = []
            
            if split_by == 'rows':
                # 按行数拆分
                total_chunks = (len(data) + chunk_size - 1) // chunk_size
                
                for i in range(total_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(data))
                    chunk_data = data.iloc[start_idx:end_idx]
                    
                    output_file = output_path / f"{base_name}_part_{i+1:03d}{extension}"
                    
                    # 写入数据块
                    write_method = getattr(self, f'write_{input_format}')
                    write_method(chunk_data, str(output_file))
                    
                    split_files.append(str(output_file))
            
            elif split_by == 'column':
                # 按列拆分
                column_name = kwargs.get('column_name')
                if not column_name or column_name not in data.columns:
                    raise ValueError(f"列 '{column_name}' 不存在")
                
                unique_values = data[column_name].unique()
                
                for value in unique_values:
                    chunk_data = data[data[column_name] == value]
                    safe_value = str(value).replace('/', '_').replace('\\', '_')
                    output_file = output_path / f"{base_name}_{safe_value}{extension}"
                    
                    # 写入数据块
                    write_method = getattr(self, f'write_{input_format}')
                    write_method(chunk_data, str(output_file))
                    
                    split_files.append(str(output_file))
            
            self.operations_log.append(f"拆分: {input_file} -> {len(split_files)} 个文件")
            
            return {
                'split_files': split_files,
                'total_files': len(split_files),
                'success': True
            }
            
        except Exception as e:
            error_msg = f"拆分文件 {input_file} 时出错: {str(e)}"
            self.errors.append(error_msg)
            return {'success': False, 'error': error_msg}
    
    def get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        try:
            file_format = self.detect_format(file_path)
            if file_format == 'unknown':
                return {'error': '不支持的文件格式'}
            
            read_method = getattr(self, f'read_{file_format}')
            data = read_method(file_path)
            
            info = {
                'file_path': file_path,
                'format': file_format,
                'size': os.path.getsize(file_path)
            }
            
            if isinstance(data, pd.DataFrame):
                info.update({
                    'rows': len(data),
                    'columns': len(data.columns),
                    'column_names': list(data.columns),
                    'data_types': data.dtypes.to_dict()
                })
            elif isinstance(data, list):
                info.update({
                    'items': len(data),
                    'type': 'list'
                })
            elif isinstance(data, dict):
                info.update({
                    'keys': list(data.keys()),
                    'type': 'dict'
                })
            
            return info
            
        except Exception as e:
            return {'error': f"读取文件信息时出错: {str(e)}"}
    
    def get_report(self) -> Dict:
        """获取转换报告"""
        return {
            'converted_files': self.converted_files,
            'errors': self.errors,
            'operations_log': self.operations_log,
            'total_converted': len(self.converted_files),
            'total_errors': len(self.errors)
        }
    
    def display_report(self):
        """显示转换报告"""
        report = self.get_report()
        
        # 创建统计表格
        table = Table(title="📊 数据转换报告")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="magenta")
        
        table.add_row("转换成功", str(report['total_converted']))
        table.add_row("转换失败", str(report['total_errors']))
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
    parser = argparse.ArgumentParser(description="数据转换工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 转换命令
    convert_parser = subparsers.add_parser('convert', help='转换单个文件')
    convert_parser.add_argument('input_file', help='输入文件')
    convert_parser.add_argument('output_file', help='输出文件')
    
    # 批量转换命令
    batch_parser = subparsers.add_parser('batch', help='批量转换文件')
    batch_parser.add_argument('input_dir', help='输入目录')
    batch_parser.add_argument('output_dir', help='输出目录')
    batch_parser.add_argument('input_format', help='输入格式')
    batch_parser.add_argument('output_format', help='输出格式')
    
    # 合并命令
    merge_parser = subparsers.add_parser('merge', help='合并文件')
    merge_parser.add_argument('output_file', help='输出文件')
    merge_parser.add_argument('input_files', nargs='+', help='输入文件列表')
    
    # 拆分命令
    split_parser = subparsers.add_parser('split', help='拆分文件')
    split_parser.add_argument('input_file', help='输入文件')
    split_parser.add_argument('output_dir', help='输出目录')
    split_parser.add_argument('--by', choices=['rows', 'column'], default='rows', help='拆分方式')
    split_parser.add_argument('--size', type=int, default=1000, help='块大小（行数）')
    split_parser.add_argument('--column', help='拆分列名（按列拆分时使用）')
    
    # 信息命令
    info_parser = subparsers.add_parser('info', help='查看文件信息')
    info_parser.add_argument('file_path', help='文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    converter = DataConverter()
    
    try:
        if args.command == 'convert':
            console.print(f"🔄 转换文件: {args.input_file} -> {args.output_file}")
            success = converter.convert_file(args.input_file, args.output_file)
            if success:
                console.print("✅ 转换完成")
            else:
                console.print("❌ 转换失败")
        
        elif args.command == 'batch':
            console.print(f"🔄 批量转换: {args.input_dir} -> {args.output_dir}")
            result = converter.batch_convert(
                args.input_dir, args.output_dir,
                args.input_format, args.output_format
            )
            console.print(f"✅ 转换完成: {result['converted']}/{result['total_files']} 个文件")
        
        elif args.command == 'merge':
            console.print(f"🔗 合并文件: {len(args.input_files)} 个文件 -> {args.output_file}")
            success = converter.merge_files(args.input_files, args.output_file)
            if success:
                console.print("✅ 合并完成")
            else:
                console.print("❌ 合并失败")
        
        elif args.command == 'split':
            console.print(f"✂️ 拆分文件: {args.input_file}")
            kwargs = {}
            if args.by == 'column':
                kwargs['column_name'] = args.column
            
            result = converter.split_file(
                args.input_file, args.output_dir,
                split_by=args.by, chunk_size=args.size, **kwargs
            )
            
            if result['success']:
                console.print(f"✅ 拆分完成: {result['total_files']} 个文件")
            else:
                console.print(f"❌ 拆分失败: {result['error']}")
        
        elif args.command == 'info':
            console.print(f"📋 文件信息: {args.file_path}")
            info = converter.get_file_info(args.file_path)
            
            if 'error' in info:
                console.print(f"❌ {info['error']}")
            else:
                # 显示文件信息
                table = Table(title="文件信息")
                table.add_column("属性", style="cyan")
                table.add_column("值", style="magenta")
                
                for key, value in info.items():
                    if key not in ['column_names', 'data_types']:
                        table.add_row(key, str(value))
                
                console.print(table)
                
                # 显示列信息（如果有）
                if 'column_names' in info:
                    console.print(f"\n📊 列信息 ({len(info['column_names'])} 列):")
                    for col in info['column_names'][:10]:  # 显示前10列
                        dtype = info.get('data_types', {}).get(col, 'unknown')
                        console.print(f"  • {col}: {dtype}")
                    
                    if len(info['column_names']) > 10:
                        console.print(f"  ... 还有 {len(info['column_names']) - 10} 列")
        
        # 显示报告
        converter.display_report()
        
    except KeyboardInterrupt:
        console.print("\n⚠️ 操作被用户取消")
    except Exception as e:
        console.print(f"\n❌ 执行失败: {str(e)}")


if __name__ == "__main__":
    main()