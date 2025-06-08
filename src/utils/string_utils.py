"""
字符串处理工具模块
"""

import re
import json
from typing import List, Dict, Any, Optional

class StringUtils:
    """字符串处理工具类"""
    
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """
        驼峰命名转下划线命名
        
        Args:
            name: 驼峰命名字符串
            
        Returns:
            str: 下划线命名字符串
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def snake_to_camel(name: str, capitalize_first: bool = False) -> str:
        """
        下划线命名转驼峰命名
        
        Args:
            name: 下划线命名字符串
            capitalize_first: 是否首字母大写
            
        Returns:
            str: 驼峰命名字符串
        """
        components = name.split('_')
        if capitalize_first:
            return ''.join(word.capitalize() for word in components)
        else:
            return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    @staticmethod
    def clean_whitespace(text: str) -> str:
        """
        清理多余的空白字符
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 替换多个空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        # 去除首尾空白
        return text.strip()
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        从文本中提取邮箱地址
        
        Args:
            text: 文本内容
            
        Returns:
            List[str]: 邮箱地址列表
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        从文本中提取URL
        
        Args:
            text: 文本内容
            
        Returns:
            List[str]: URL列表
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        截断文本
        
        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 截断后缀
            
        Returns:
            str: 截断后的文本
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def mask_sensitive_info(text: str, mask_char: str = "*") -> str:
        """
        遮蔽敏感信息
        
        Args:
            text: 原始文本
            mask_char: 遮蔽字符
            
        Returns:
            str: 遮蔽后的文本
        """
        # 遮蔽邮箱
        text = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[A-Z|a-z]{2,})', 
                     lambda m: f"{m.group(1)[:2]}{mask_char * 3}@{m.group(2)}", text)
        
        # 遮蔽手机号
        text = re.sub(r'(\d{3})\d{4}(\d{4})', rf'\1{mask_char * 4}\2', text)
        
        # 遮蔽身份证号
        text = re.sub(r'(\d{6})\d{8}(\d{4})', rf'\1{mask_char * 8}\2', text)
        
        return text
    
    @staticmethod
    def validate_json(text: str) -> bool:
        """
        验证JSON格式
        
        Args:
            text: JSON字符串
            
        Returns:
            bool: 是否为有效JSON
        """
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def format_json(text: str, indent: int = 2) -> Optional[str]:
        """
        格式化JSON字符串
        
        Args:
            text: JSON字符串
            indent: 缩进空格数
            
        Returns:
            Optional[str]: 格式化后的JSON字符串，失败返回None
        """
        try:
            data = json.loads(text)
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def count_words(text: str) -> Dict[str, int]:
        """
        统计单词频率
        
        Args:
            text: 文本内容
            
        Returns:
            Dict[str, int]: 单词频率字典
        """
        # 提取单词（只保留字母和数字）
        words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
        
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        return word_count
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """
        移除HTML标签
        
        Args:
            text: 包含HTML的文本
            
        Returns:
            str: 移除HTML标签后的文本
        """
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)