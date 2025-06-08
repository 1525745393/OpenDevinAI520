"""
数据转换工具
"""

import json
import csv
import xml.etree.ElementTree as ET
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.utils.logger import setup_logger

class DataConverter:
    """数据转换工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据转换工具
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = setup_logger("DataConverter")
    
    def get_description(self) -> str:
        """获取工具描述"""
        return "数据转换工具 - 支持JSON、CSV、XML、YAML等格式互转"
    
    def execute(self, action: str, args: List[str]) -> Optional[str]:
        """
        执行工具操作
        
        Args:
            action: 操作名称
            args: 参数列表
            
        Returns:
            Optional[str]: 执行结果
        """
        if action == "json_to_csv":
            return self._json_to_csv(args)
        elif action == "csv_to_json":
            return self._csv_to_json(args)
        elif action == "json_to_xml":
            return self._json_to_xml(args)
        elif action == "xml_to_json":
            return self._xml_to_json(args)
        elif action == "json_to_yaml":
            return self._json_to_yaml(args)
        elif action == "yaml_to_json":
            return self._yaml_to_json(args)
        elif action == "csv_to_xml":
            return self._csv_to_xml(args)
        elif action == "xml_to_csv":
            return self._xml_to_csv(args)
        elif action == "format_json":
            return self._format_json(args)
        elif action == "minify_json":
            return self._minify_json(args)
        elif action == "help":
            return self._show_help()
        else:
            return f"未知操作: {action}"
    
    def _json_to_csv(self, args: List[str]) -> str:
        """
        JSON转CSV
        
        Args:
            args: 参数列表 [input_file, output_file]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: json_to_csv <输入文件> <输出文件>"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 确保数据是列表格式
            if not isinstance(data, list):
                return "JSON数据必须是对象数组格式"
            
            if not data:
                return "JSON数据为空"
            
            # 获取所有字段名
            fieldnames = set()
            for item in data:
                if isinstance(item, dict):
                    fieldnames.update(item.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            # 写入CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data:
                    if isinstance(item, dict):
                        # 填充缺失的字段
                        row = {field: item.get(field, '') for field in fieldnames}
                        writer.writerow(row)
            
            self.logger.info(f"JSON转CSV完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {len(data)} 条记录已写入 {output_file}"
        
        except json.JSONDecodeError as e:
            return f"❌ JSON格式错误: {e}"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _csv_to_json(self, args: List[str]) -> str:
        """
        CSV转JSON
        
        Args:
            args: 参数列表 [input_file, output_file]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: csv_to_json <输入文件> <输出文件>"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            data = []
            
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 尝试转换数值类型
                    converted_row = {}
                    for key, value in row.items():
                        if value.isdigit():
                            converted_row[key] = int(value)
                        elif self._is_float(value):
                            converted_row[key] = float(value)
                        elif value.lower() in ('true', 'false'):
                            converted_row[key] = value.lower() == 'true'
                        else:
                            converted_row[key] = value
                    data.append(converted_row)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"CSV转JSON完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {len(data)} 条记录已写入 {output_file}"
        
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _json_to_xml(self, args: List[str]) -> str:
        """
        JSON转XML
        
        Args:
            args: 参数列表 [input_file, output_file, root_name]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: json_to_xml <输入文件> <输出文件> [根元素名]"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        root_name = args[2] if len(args) > 2 else "root"
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 创建XML根元素
            root = ET.Element(root_name)
            
            # 递归转换JSON到XML
            self._json_to_xml_element(data, root)
            
            # 格式化XML
            self._indent_xml(root)
            
            # 写入文件
            tree = ET.ElementTree(root)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"JSON转XML完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {output_file}"
        
        except json.JSONDecodeError as e:
            return f"❌ JSON格式错误: {e}"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _xml_to_json(self, args: List[str]) -> str:
        """
        XML转JSON
        
        Args:
            args: 参数列表 [input_file, output_file]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: xml_to_json <输入文件> <输出文件>"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            
            # 转换XML到字典
            data = self._xml_element_to_dict(root)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"XML转JSON完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {output_file}"
        
        except ET.ParseError as e:
            return f"❌ XML格式错误: {e}"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _json_to_yaml(self, args: List[str]) -> str:
        """
        JSON转YAML
        
        Args:
            args: 参数列表 [input_file, output_file]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: json_to_yaml <输入文件> <输出文件>"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            self.logger.info(f"JSON转YAML完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {output_file}"
        
        except json.JSONDecodeError as e:
            return f"❌ JSON格式错误: {e}"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _yaml_to_json(self, args: List[str]) -> str:
        """
        YAML转JSON
        
        Args:
            args: 参数列表 [input_file, output_file]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: yaml_to_json <输入文件> <输出文件>"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"YAML转JSON完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {output_file}"
        
        except yaml.YAMLError as e:
            return f"❌ YAML格式错误: {e}"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _csv_to_xml(self, args: List[str]) -> str:
        """
        CSV转XML
        
        Args:
            args: 参数列表 [input_file, output_file, root_name, item_name]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: csv_to_xml <输入文件> <输出文件> [根元素名] [项目元素名]"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        root_name = args[2] if len(args) > 2 else "data"
        item_name = args[3] if len(args) > 3 else "item"
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            root = ET.Element(root_name)
            
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    item_element = ET.SubElement(root, item_name)
                    for key, value in row.items():
                        field_element = ET.SubElement(item_element, key.replace(' ', '_'))
                        field_element.text = str(value)
            
            # 格式化XML
            self._indent_xml(root)
            
            # 写入文件
            tree = ET.ElementTree(root)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"CSV转XML完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {output_file}"
        
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _xml_to_csv(self, args: List[str]) -> str:
        """
        XML转CSV
        
        Args:
            args: 参数列表 [input_file, output_file, item_xpath]
            
        Returns:
            str: 转换结果
        """
        if len(args) < 2:
            return "参数不足。用法: xml_to_csv <输入文件> <输出文件> [项目XPath]"
        
        input_file = Path(args[0])
        output_file = Path(args[1])
        item_xpath = args[2] if len(args) > 2 else "./*"
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            
            # 查找所有项目元素
            items = root.findall(item_xpath)
            
            if not items:
                return "未找到匹配的XML元素"
            
            # 收集所有字段名
            fieldnames = set()
            data = []
            
            for item in items:
                row = {}
                for child in item:
                    fieldnames.add(child.tag)
                    row[child.tag] = child.text or ''
                data.append(row)
            
            fieldnames = sorted(list(fieldnames))
            
            # 写入CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in data:
                    # 填充缺失的字段
                    complete_row = {field: row.get(field, '') for field in fieldnames}
                    writer.writerow(complete_row)
            
            self.logger.info(f"XML转CSV完成: {input_file} -> {output_file}")
            return f"✅ 转换完成: {len(data)} 条记录已写入 {output_file}"
        
        except ET.ParseError as e:
            return f"❌ XML格式错误: {e}"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    def _format_json(self, args: List[str]) -> str:
        """
        格式化JSON文件
        
        Args:
            args: 参数列表 [input_file, output_file, indent]
            
        Returns:
            str: 格式化结果
        """
        if not args:
            return "请指定输入文件"
        
        input_file = Path(args[0])
        output_file = Path(args[1]) if len(args) > 1 else input_file
        indent = int(args[2]) if len(args) > 2 else 2
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            self.logger.info(f"JSON格式化完成: {input_file} -> {output_file}")
            return f"✅ JSON格式化完成: {output_file}"
        
        except json.JSONDecodeError as e:
            return f"❌ JSON格式错误: {e}"
        except Exception as e:
            return f"❌ 格式化失败: {e}"
    
    def _minify_json(self, args: List[str]) -> str:
        """
        压缩JSON文件
        
        Args:
            args: 参数列表 [input_file, output_file]
            
        Returns:
            str: 压缩结果
        """
        if not args:
            return "请指定输入文件"
        
        input_file = Path(args[0])
        output_file = Path(args[1]) if len(args) > 1 else input_file
        
        if not input_file.exists():
            return f"输入文件不存在: {input_file}"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
            
            # 计算压缩比
            original_size = input_file.stat().st_size
            compressed_size = output_file.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            self.logger.info(f"JSON压缩完成: {input_file} -> {output_file}")
            return f"✅ JSON压缩完成: {output_file} (压缩率: {compression_ratio:.1f}%)"
        
        except json.JSONDecodeError as e:
            return f"❌ JSON格式错误: {e}"
        except Exception as e:
            return f"❌ 压缩失败: {e}"
    
    def _json_to_xml_element(self, data: Any, parent: ET.Element):
        """
        递归将JSON数据转换为XML元素
        
        Args:
            data: JSON数据
            parent: 父XML元素
        """
        if isinstance(data, dict):
            for key, value in data.items():
                # 清理元素名称
                clean_key = str(key).replace(' ', '_').replace('-', '_')
                element = ET.SubElement(parent, clean_key)
                self._json_to_xml_element(value, element)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                element = ET.SubElement(parent, f"item_{i}")
                self._json_to_xml_element(item, element)
        else:
            parent.text = str(data) if data is not None else ""
    
    def _xml_element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        将XML元素转换为字典
        
        Args:
            element: XML元素
            
        Returns:
            Dict[str, Any]: 转换后的字典
        """
        result = {}
        
        # 处理属性
        if element.attrib:
            result.update(element.attrib)
        
        # 处理子元素
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._xml_element_to_dict(child)
                if child.tag in child_dict:
                    # 如果已存在同名元素，转换为列表
                    if not isinstance(child_dict[child.tag], list):
                        child_dict[child.tag] = [child_dict[child.tag]]
                    child_dict[child.tag].append(child_data)
                else:
                    child_dict[child.tag] = child_data
            result.update(child_dict)
        
        # 处理文本内容
        if element.text and element.text.strip():
            if result:
                result['text'] = element.text.strip()
            else:
                return element.text.strip()
        
        return result
    
    def _indent_xml(self, elem: ET.Element, level: int = 0):
        """
        格式化XML缩进
        
        Args:
            elem: XML元素
            level: 缩进级别
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def _is_float(self, value: str) -> bool:
        """
        检查字符串是否为浮点数
        
        Args:
            value: 字符串值
            
        Returns:
            bool: 是否为浮点数
        """
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False
    
    def _show_help(self) -> str:
        """显示帮助信息"""
        return """
数据转换工具帮助:

操作:
  json_to_csv <输入> <输出>              - JSON转CSV
  csv_to_json <输入> <输出>              - CSV转JSON
  json_to_xml <输入> <输出> [根元素]      - JSON转XML
  xml_to_json <输入> <输出>              - XML转JSON
  json_to_yaml <输入> <输出>             - JSON转YAML
  yaml_to_json <输入> <输出>             - YAML转JSON
  csv_to_xml <输入> <输出> [根] [项目]    - CSV转XML
  xml_to_csv <输入> <输出> [XPath]       - XML转CSV
  format_json <输入> [输出] [缩进]        - 格式化JSON
  minify_json <输入> [输出]              - 压缩JSON
  help                                  - 显示此帮助信息

示例:
  data_converter json_to_csv data.json data.csv
  data_converter csv_to_json users.csv users.json
  data_converter json_to_xml config.json config.xml
  data_converter format_json messy.json clean.json 4
  data_converter minify_json large.json small.json

注意:
- JSON转CSV要求JSON为对象数组格式
- XML转换会自动处理元素名称中的特殊字符
- 支持自动类型检测和转换
"""