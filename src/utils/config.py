"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    config_path = Path(config_file)
    
    # 默认配置
    default_config = {
        "app": {
            "name": "OpenDevinAI520",
            "version": "1.0.0",
            "debug": False
        },
        "tools": {
            "enabled": [
                "code_formatter",
                "file_processor", 
                "api_tester",
                "data_converter",
                "media_renamer"
            ]
        },
        "logging": {
            "level": "INFO",
            "file_enabled": True
        }
    }
    
    # 如果配置文件存在，则加载并合并
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f) or {}
            
            # 合并配置
            config = merge_config(default_config, file_config)
        except Exception as e:
            print(f"警告: 配置文件加载失败 ({e})，使用默认配置")
            config = default_config
    else:
        config = default_config
        # 创建默认配置文件
        create_default_config(config_path, default_config)
    
    # 从环境变量覆盖配置
    config = override_from_env(config)
    
    return config

def merge_config(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    递归合并配置字典
    
    Args:
        default: 默认配置
        override: 覆盖配置
        
    Returns:
        Dict[str, Any]: 合并后的配置
    """
    result = default.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    
    return result

def override_from_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    从环境变量覆盖配置
    
    Args:
        config: 原始配置
        
    Returns:
        Dict[str, Any]: 覆盖后的配置
    """
    # 支持的环境变量映射
    env_mappings = {
        "OPENDEVINAI520_DEBUG": ("app", "debug"),
        "OPENDEVINAI520_LOG_LEVEL": ("logging", "level"),
    }
    
    for env_var, (section, key) in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            if section not in config:
                config[section] = {}
            
            # 类型转换
            if key == "debug":
                config[section][key] = value.lower() in ("true", "1", "yes")
            else:
                config[section][key] = value
    
    return config

def create_default_config(config_path: Path, config: Dict[str, Any]):
    """
    创建默认配置文件
    
    Args:
        config_path: 配置文件路径
        config: 配置内容
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ 已创建默认配置文件: {config_path}")
    except Exception as e:
        print(f"警告: 无法创建配置文件 ({e})")