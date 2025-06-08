"""
字符串工具测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.string_utils import StringUtils


class TestStringUtils:
    """字符串工具测试类"""
    
    def test_camel_to_snake(self):
        """测试驼峰转下划线"""
        assert StringUtils.camel_to_snake("CamelCase") == "camel_case"
        assert StringUtils.camel_to_snake("camelCase") == "camel_case"
        assert StringUtils.camel_to_snake("XMLHttpRequest") == "xml_http_request"
        assert StringUtils.camel_to_snake("iPhone") == "i_phone"
    
    def test_snake_to_camel(self):
        """测试下划线转驼峰"""
        assert StringUtils.snake_to_camel("snake_case") == "snakeCase"
        assert StringUtils.snake_to_camel("snake_case", True) == "SnakeCase"
        assert StringUtils.snake_to_camel("xml_http_request") == "xmlHttpRequest"
        assert StringUtils.snake_to_camel("single") == "single"
    
    def test_clean_whitespace(self):
        """测试清理空白字符"""
        assert StringUtils.clean_whitespace("  hello   world  ") == "hello world"
        assert StringUtils.clean_whitespace("hello\n\tworld") == "hello world"
        assert StringUtils.clean_whitespace("   ") == ""
    
    def test_extract_emails(self):
        """测试提取邮箱"""
        text = "联系我们：admin@example.com 或 support@test.org"
        emails = StringUtils.extract_emails(text)
        assert "admin@example.com" in emails
        assert "support@test.org" in emails
        assert len(emails) == 2
    
    def test_extract_urls(self):
        """测试提取URL"""
        text = "访问 https://example.com 或 http://test.org/path"
        urls = StringUtils.extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org/path" in urls
        assert len(urls) == 2
    
    def test_truncate(self):
        """测试截断文本"""
        text = "这是一个很长的文本"
        assert StringUtils.truncate(text, 10) == "这是一个很长的..."
        assert StringUtils.truncate(text, 20) == text
        assert StringUtils.truncate(text, 10, ">>") == "这是一个很长的文>>"
    
    def test_mask_sensitive_info(self):
        """测试遮蔽敏感信息"""
        text = "邮箱：test@example.com 手机：13812345678"
        masked = StringUtils.mask_sensitive_info(text)
        assert "te***@example.com" in masked
        assert "138****5678" in masked
    
    def test_validate_json(self):
        """测试JSON验证"""
        assert StringUtils.validate_json('{"key": "value"}') == True
        assert StringUtils.validate_json('{"key": value}') == False
        assert StringUtils.validate_json('invalid json') == False
    
    def test_format_json(self):
        """测试JSON格式化"""
        json_str = '{"key":"value","nested":{"a":1}}'
        formatted = StringUtils.format_json(json_str)
        assert formatted is not None
        assert "  " in formatted  # 检查缩进
        
        invalid_json = '{"key": value}'
        assert StringUtils.format_json(invalid_json) is None
    
    def test_count_words(self):
        """测试单词统计"""
        text = "hello world hello python"
        word_count = StringUtils.count_words(text)
        assert word_count["hello"] == 2
        assert word_count["world"] == 1
        assert word_count["python"] == 1
    
    def test_remove_html_tags(self):
        """测试移除HTML标签"""
        html = "<p>Hello <b>world</b>!</p>"
        clean = StringUtils.remove_html_tags(html)
        assert clean == "Hello world!"
        
        html_complex = '<div class="test"><span>Text</span></div>'
        clean_complex = StringUtils.remove_html_tags(html_complex)
        assert clean_complex == "Text"