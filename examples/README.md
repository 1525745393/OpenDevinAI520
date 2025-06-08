# 示例文件

本目录包含了 OpenDevinAI520 各种工具的示例文件和配置。

## 文件说明

### API测试示例
- `api_test_config.json` - API批量测试配置文件示例
  - 包含多个测试用例
  - 演示GET和POST请求
  - 使用JSONPlaceholder作为测试API

### 数据转换示例
- `sample_data.json` - 示例JSON数据文件
  - 包含员工信息数据
  - 可用于测试JSON到CSV/XML转换
  - 演示中文数据处理

### 代码格式化示例
- `sample_code.py` - 未格式化的Python代码
  - 包含各种格式问题
  - 可用于测试代码格式化工具
  - 演示格式化前后的对比

## 使用方法

### 1. API测试
```bash
# 批量测试API
api_tester batch_test examples/api_test_config.json

# 单个API测试
api_tester test https://jsonplaceholder.typicode.com/users
```

### 2. 数据转换
```bash
# JSON转CSV
data_converter json_to_csv examples/sample_data.json output.csv

# JSON转XML
data_converter json_to_xml examples/sample_data.json output.xml employees

# 格式化JSON
data_converter format_json examples/sample_data.json formatted.json 4
```

### 3. 代码格式化
```bash
# 格式化Python代码
code_formatter format examples/sample_code.py

# 检查代码格式
code_formatter check examples/sample_code.py
```

### 4. 影视文件重命名
```bash
# 创建测试文件
mkdir test_media
touch "test_media/The.Matrix.1999.1080p.BluRay.x264.mp4"
touch "test_media/Friends.S01E01.720p.HDTV.x264.mp4"

# 自动重命名
media_renamer auto_rename test_media/

# 分析文件
media_renamer analyze test_media/
```

### 5. 文件批量处理
```bash
# 创建测试文件
mkdir test_files
touch test_files/file1.txt test_files/file2.txt test_files/document.pdf

# 批量重命名
file_processor batch_rename "test_files/*.txt" "backup_*.txt"

# 组织文件
file_processor organize test_files/
```

## 注意事项

1. 运行示例前请确保已安装所有依赖
2. 某些示例需要网络连接（如API测试）
3. 文件操作示例会修改文件，请在测试目录中运行
4. 建议先在示例文件上测试，再在实际文件上使用

## 扩展示例

您可以基于这些示例创建自己的配置文件和测试数据：

1. 修改API测试配置以测试您的API
2. 使用您的数据文件测试数据转换
3. 在您的代码库上测试格式化工具
4. 使用您的媒体文件测试重命名功能