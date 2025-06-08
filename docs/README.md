# OpenDevinAI520 文档

欢迎使用 OpenDevinAI520 实用工具开发平台！

## 📚 文档目录

- [快速开始](quick-start.md)
- [工具指南](tools-guide.md)
- [API文档](api-reference.md)
- [配置说明](configuration.md)
- [开发指南](development.md)
- [贡献指南](contributing.md)

## 🛠️ 工具概览

### 代码格式化工具 (CodeFormatter)
- 支持多种编程语言的代码格式化
- 自动检测文件类型
- 批量处理功能

### 文件批量处理工具 (FileProcessor)
- 批量重命名、复制、移动文件
- 查找重复文件
- 按类型组织文件
- 清理临时文件

### API测试工具 (ApiTester)
- HTTP API接口测试
- 批量测试支持
- 负载测试功能
- API监控和报告生成

### 数据转换工具 (DataConverter)
- JSON、CSV、XML、YAML格式互转
- 数据格式化和压缩
- 智能类型检测

### 影视文件重命名工具 (MediaRenamer)
- 智能识别电影和电视剧文件
- 自动提取标题、年份、季集信息
- 支持自定义命名模式
- 文件组织功能

## 🚀 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**
   ```bash
   python src/main.py
   ```

3. **查看帮助**
   ```
   OpenDevinAI520> help
   ```

## 💡 使用示例

### 格式化代码
```
code_formatter format src/
```

### 重命名影视文件
```
media_renamer auto_rename ./downloads/
```

### 转换数据格式
```
data_converter json_to_csv data.json data.csv
```

### 测试API
```
api_tester test https://api.example.com/users
```

## 🔧 配置

项目使用 `config.yaml` 文件进行配置，支持环境变量覆盖。

详细配置说明请参考 [配置文档](configuration.md)。

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](contributing.md) 了解如何参与项目开发。

## 📄 许可证

本项目采用 MIT 许可证，详情请查看 [LICENSE](../LICENSE) 文件。

---

**人人为我，我为人人 - 让我们一起构建更好的开发工具生态！**