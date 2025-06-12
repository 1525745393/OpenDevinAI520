# 智能影视重命名工具 - 增强版

## 🎬 项目概述

这是一个集成TMDb和豆瓣API的智能影视文件重命名工具，能够自动获取准确的影视元数据，生成NFO文件，下载海报，为你的媒体库提供完整的元数据支持。

### ✨ 核心特性

- **🌐 双API集成**: TMDb + 豆瓣，获取最全面的影视数据
- **🎯 智能匹配**: 先进算法自动选择最佳匹配结果
- **📄 元数据生成**: 支持标准NFO格式和群晖vsmeta格式
- **🖼️ 海报下载**: 自动下载高质量海报和背景图
- **💾 智能缓存**: 避免重复API调用，提升处理速度
- **🏠 群晖优化**: 专为群晖Video Station设计
- **💻 跨平台**: 支持Windows、macOS、Linux、群晖NAS

## 🚀 快速开始

### 方法一：自动安装（推荐）

```bash
# 下载并运行安装脚本
chmod +x install_enhanced_renamer.sh
./install_enhanced_renamer.sh
```

### 方法二：直接运行

```bash
# 运行增强版工具
python3 video_renamer_enhanced.py

# 运行演示程序
python3 video_renamer_enhanced_demo.py
```

## 📋 文件说明

| 文件名 | 说明 |
|--------|------|
| `video_renamer_enhanced.py` | 🎯 **主程序** - 增强版重命名工具 |
| `video_renamer.py` | 📦 **依赖** - 基础重命名功能（必需） |
| `video_renamer_enhanced_demo.py` | 🎮 **演示** - 功能演示和测试 |
| `vsmeta_generator.py` | 📄 **vsmeta** - 群晖Video Station元数据生成器 |
| `install_enhanced_renamer.sh` | 🔧 **安装** - 自动安装脚本 |
| `API_SETUP_GUIDE.md` | 📖 **配置** - API设置详细指南 |
| `VSMETA_FORMAT_GUIDE.md` | 📋 **vsmeta** - 群晖vsmeta格式详细说明 |
| `ENHANCED_README.md` | 📚 **文档** - 完整功能文档 |

## ⚙️ API配置

### 🎭 TMDb API（推荐）
1. 访问 [TMDb API页面](https://www.themoviedb.org/settings/api)
2. 注册免费账户并申请API密钥
3. 在程序中配置：菜单 4 → 1 → 输入API密钥

### 🎪 豆瓣API
1. 在程序中启用：菜单 4 → 2
2. 无需API密钥，但有访问频率限制

## 🎨 重命名示例

### 电影重命名

**原始文件名:**
```
The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv
```

**增强版重命名后:**
```
黑客帝国 The Matrix (1999) [1080p] [BluRay] [评分8.7].mkv
```

### 电视剧重命名

**原始文件名:**
```
Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv
```

**增强版重命名后:**
```
权力的游戏 Game of Thrones S01E01 [1080p] [BluRay] [评分9.3].mkv
```

## 📄 生成的文件

### 群晖vsmeta元数据文件（推荐）
```json
{
  "version": "1",
  "type": "movie",
  "title": "The Matrix",
  "title_local": "黑客帝国",
  "summary": "一名年轻的程序员被神秘的黑客墨菲斯联系...",
  "rating": 8.7,
  "year": 1999,
  "genre": ["科幻", "动作"],
  "extra": {
    "tmdb": {"id": 603, "rating": 8.2},
    "douban": {"id": "1291843", "rating": 9.0}
  }
}
```

### 标准NFO元数据文件
```xml
<?xml version='1.0' encoding='utf-8'?>
<movie>
  <title>黑客帝国</title>
  <originaltitle>The Matrix</originaltitle>
  <year>1999</year>
  <rating name="tmdb" max="10">
    <value>8.7</value>
  </rating>
  <!-- 更多元数据... -->
</movie>
```

### 海报文件
```
电影名-poster.jpg    # 竖版海报
电影名-fanart.jpg    # 横版背景图
```

## 🔧 增强版模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{chinese_title}` | 中文标题 | 黑客帝国 |
| `{title}` | 英文标题 | The Matrix |
| `{tmdb_rating}` | TMDb评分 | 8.7 |
| `{douban_rating}` | 豆瓣评分 | 9.0 |
| `{rating}` | 最佳评分 | 9.0 |
| `{director}` | 导演 | 沃卓斯基姐妹 |
| `{genre}` | 类型 | 科幻, 动作 |

## 🏠 群晖NAS专用功能

- **Video Station集成**: 完美支持群晖Video Station
- **vsmeta格式**: 群晖原生元数据格式，显示效果最佳
- **目录结构**: 自动创建标准媒体库结构
- **中文支持**: vsmeta格式对中文标题支持优秀
- **海报显示**: 海报在Video Station中正确显示
- **任务计划**: 支持定时自动处理新文件

## 📊 功能对比

| 功能 | 基础版 | 增强版 |
|------|--------|--------|
| 文件名解析 | ✅ | ✅ |
| 重命名模板 | ✅ | ✅ |
| **API元数据获取** | ❌ | ✅ |
| **元数据文件生成** | ❌ | ✅ |
| **海报下载** | ❌ | ✅ |
| **智能匹配** | ❌ | ✅ |
| **评分信息** | ❌ | ✅ |
| **缓存机制** | ❌ | ✅ |

## 🛠️ 系统要求

- **Python**: 3.6或更高版本
- **网络**: 稳定的互联网连接（API调用需要）
- **存储**: 至少100MB可用空间
- **平台**: Windows、macOS、Linux、群晖NAS

## 📖 详细文档

- 📚 [完整功能文档](ENHANCED_README.md) - 详细的功能说明和使用指南
- 🔧 [API配置指南](API_SETUP_GUIDE.md) - TMDb和豆瓣API的详细配置步骤
- 📋 [vsmeta格式指南](VSMETA_FORMAT_GUIDE.md) - 群晖Video Station元数据格式说明
- 🎮 [演示程序](video_renamer_enhanced_demo.py) - 运行演示了解所有功能

## 🚀 使用流程

1. **安装**: 运行 `install_enhanced_renamer.sh` 自动安装
2. **配置**: 设置TMDb API密钥和豆瓣API
3. **测试**: 运行演示程序熟悉功能
4. **预览**: 使用预览模式查看重命名结果
5. **执行**: 确认无误后执行实际重命名
6. **享受**: 在媒体中心中享受完整的元数据体验

## 💡 使用建议

- 🔑 **API配置**: 建议同时配置TMDb和豆瓣API获得最佳效果
- 🔍 **预览模式**: 首次使用建议启用预览模式避免误操作
- 💾 **备份文件**: 重要文件建议先备份
- 🌐 **网络环境**: 在稳定的网络环境下使用API功能
- 📁 **批量处理**: 大量文件建议分批处理

## 🆘 故障排除

### 常见问题
- **API连接失败**: 检查网络连接和API密钥配置
- **元数据不准确**: 确保文件名包含准确的年份信息
- **NFO生成失败**: 检查目录写入权限
- **海报下载失败**: 确认网络连接和磁盘空间

### 获取帮助
1. 查看程序内置帮助（菜单选项7）
2. 阅读详细文档和API配置指南
3. 运行演示程序了解功能
4. 检查日志文件获取错误信息

---

**开始你的智能重命名之旅！** 🎉

> 💡 **提示**: 增强版功能强大但需要网络连接，建议首次使用时先在测试目录中尝试。