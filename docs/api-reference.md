# API参考文档

## 概述

OpenDevinAI520 提供了一系列实用的开发工具，每个工具都有完整的命令行接口和Python API。

## 工具列表

### 1. 代码格式化工具 (code_formatter)

#### 命令行使用

```bash
# 格式化单个文件
python -m src.tools.code_formatter file.py

# 格式化目录（递归）
python -m src.tools.code_formatter ./src --recursive

# 显示详细报告
python -m src.tools.code_formatter ./src --report
```

#### Python API

```python
from tools.code_formatter import CodeFormatter

formatter = CodeFormatter()

# 格式化单个文件
success = formatter.format_file('example.py')

# 格式化目录
result = formatter.format_directory('./src', recursive=True)

# 获取报告
report = formatter.get_report()
```

#### 支持的语言

| 语言 | 扩展名 | 格式化工具 | 安装命令 |
|------|--------|------------|----------|
| Python | .py | black | `pip install black` |
| JavaScript | .js, .jsx | prettier | `npm install -g prettier` |
| TypeScript | .ts, .tsx | prettier | `npm install -g prettier` |
| JSON | .json | 内置 | 无需安装 |
| CSS | .css, .scss, .sass | prettier | `npm install -g prettier` |

### 2. 文件批量处理工具 (file_processor)

#### 命令行使用

```bash
# 批量重命名（预览模式）
python -m tools.file_processor rename ./files "old_pattern" "new_pattern" --preview

# 批量重命名（执行）
python -m tools.file_processor rename ./files "(\d+)_old" "\\1_new"

# 批量复制
python -m tools.file_processor copy ./source ./target --pattern "*.txt"

# 批量移动
python -m tools.file_processor move ./source ./target --pattern "*.log" --overwrite

# 按扩展名组织文件
python -m tools.file_processor organize ./downloads

# 清理空目录
python -m tools.file_processor clean ./project
```

#### Python API

```python
from tools.file_processor import FileProcessor

processor = FileProcessor()

# 批量重命名
result = processor.batch_rename('./files', r'old_(\d+)', r'new_\1')

# 批量复制
result = processor.batch_copy('./source', './target', '*.txt')

# 组织文件
result = processor.organize_by_extension('./downloads')

# 获取报告
report = processor.get_report()
```

#### 重命名模式示例

| 原文件名 | 正则模式 | 替换模式 | 新文件名 |
|----------|----------|----------|----------|
| `old_001.txt` | `old_(\d+)` | `new_\1` | `new_001.txt` |
| `IMG_20231201.jpg` | `IMG_(\d{8})` | `photo_\1` | `photo_20231201.jpg` |
| `document.pdf` | `(.+)\.pdf` | `\1_backup.pdf` | `document_backup.pdf` |

### 3. API测试工具 (api_tester)

#### 命令行使用

```bash
# 测试单个API
python -m tools.api_tester test GET /api/users --base-url https://api.example.com

# 使用认证
python -m tools.api_tester test GET /api/profile \
  --base-url https://api.example.com \
  --auth-type bearer \
  --token "your_token_here"

# POST请求
python -m tools.api_tester test POST /api/users \
  --base-url https://api.example.com \
  --data '{"name": "John", "email": "john@example.com"}'

# 批量测试
python -m tools.api_tester batch test_suite.json \
  --output results.json \
  --report report.html
```

#### Python API

```python
from tools.api_tester import APITester

tester = APITester(base_url='https://api.example.com')

# 设置认证
tester.set_auth('bearer', token='your_token')

# 测试单个端点
result = tester.test_endpoint(
    method='GET',
    endpoint='/api/users',
    expected_status=200
)

# 批量测试
test_cases = [
    {
        'name': '获取用户列表',
        'method': 'GET',
        'endpoint': '/api/users',
        'expected_status': 200
    },
    {
        'name': '创建用户',
        'method': 'POST',
        'endpoint': '/api/users',
        'data': {'name': 'John', 'email': 'john@example.com'},
        'expected_status': 201
    }
]

results = tester.batch_test(test_cases)
```

#### 测试套件格式

```json
[
  {
    "name": "获取用户列表",
    "method": "GET",
    "endpoint": "/api/users",
    "expected_status": 200,
    "headers": {
      "Accept": "application/json"
    }
  },
  {
    "name": "创建用户",
    "method": "POST",
    "endpoint": "/api/users",
    "data": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "expected_status": 201
  },
  {
    "name": "获取用户详情",
    "method": "GET",
    "endpoint": "/api/users/1",
    "expected_status": 200
  }
]
```

## 通用参数

### 认证方式

#### Bearer Token
```bash
--auth-type bearer --token "your_token_here"
```

#### Basic认证
```bash
--auth-type basic --username "user" --password "pass"
```

#### API Key
```bash
--auth-type apikey --api-key "your_key" --header-name "X-API-Key"
```

### 输出格式

所有工具都支持以下输出选项：

- `--verbose`: 详细输出
- `--quiet`: 静默模式
- `--json`: JSON格式输出
- `--report`: 生成详细报告

## 错误处理

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 1 | 参数错误 | 检查命令行参数 |
| 2 | 文件不存在 | 确认文件路径正确 |
| 3 | 权限不足 | 检查文件权限 |
| 4 | 网络错误 | 检查网络连接 |
| 5 | 格式化工具未安装 | 安装相应的格式化工具 |

### 调试技巧

1. 使用 `--verbose` 参数获取详细信息
2. 使用 `--preview` 参数预览操作结果
3. 检查工具的依赖是否正确安装
4. 查看生成的日志文件

## 扩展开发

## 新增工具

### 4. 影视文件重命名工具 (media_renamer)

智能识别并重命名电影、电视剧文件。

#### 命令行使用

```bash
# 重命名媒体文件（预览模式）
python -m src.tools.media_renamer rename ./media --preview

# 实际重命名
python -m src.tools.media_renamer rename ./media

# 按类型组织文件
python -m src.tools.media_renamer organize ./media
```

#### 支持的格式
- 视频文件：.mp4, .mkv, .avi, .mov, .wmv, .flv, .webm 等
- 命名模式：S01E01, 1x01, 年份识别, 质量标识等

### 5. 数据转换工具 (data_converter)

支持多种数据格式之间的转换。

#### 命令行使用

```bash
# 单文件转换
python -m src.tools.data_converter convert input.csv output.json

# 批量转换
python -m src.tools.data_converter batch ./input_dir ./output_dir csv json

# 合并文件
python -m src.tools.data_converter merge output.json file1.json file2.json

# 拆分文件
python -m src.tools.data_converter split large_file.csv ./output_dir --by rows --size 1000
```

#### 支持的格式
- JSON, CSV, XML, YAML, Excel, TSV, Parquet, HTML

### 6. 开发环境配置工具 (env_configurator)

快速配置各种开发环境。

#### 命令行使用

```bash
# 查看系统信息
python -m src.tools.env_configurator info

# 配置Python环境
python -m src.tools.env_configurator python ./my_project

# 配置Node.js环境
python -m src.tools.env_configurator nodejs ./my_app

# 完整环境配置
python -m src.tools.env_configurator full ./my_project --type python
```

### 添加新工具

1. 在 `src/tools/` 目录创建新的Python文件
2. 实现工具类和命令行接口
3. 更新 `src/main.py` 中的工具列表
4. 添加相应的测试和文档

### 工具模板

```python
#!/usr/bin/env python3
"""
新工具模板
"""

from rich.console import Console

console = Console()

class NewTool:
    """新工具类"""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    def process(self, input_data):
        """处理逻辑"""
        try:
            # 实现具体功能
            result = self._do_process(input_data)
            self.results.append(result)
            return result
        except Exception as e:
            self.errors.append(str(e))
            return None
    
    def _do_process(self, input_data):
        """具体处理逻辑"""
        pass
    
    def get_report(self):
        """获取处理报告"""
        return {
            'results': self.results,
            'errors': self.errors,
            'total_processed': len(self.results),
            'total_errors': len(self.errors)
        }

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="新工具")
    parser.add_argument('input', help='输入参数')
    
    args = parser.parse_args()
    
    tool = NewTool()
    result = tool.process(args.input)
    
    if result:
        console.print("✅ 处理完成", style="green")
    else:
        console.print("❌ 处理失败", style="red")

if __name__ == "__main__":
    main()
```

---

更多信息请参考：
- [快速开始指南](getting-started.md)
- [工具使用指南](tools-guide.md)
- [贡献指南](contributing.md)