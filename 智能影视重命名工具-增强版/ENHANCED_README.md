# 智能影视文件重命名工具 - 增强版

## 📖 项目简介

这是一个集成TMDb和豆瓣API的智能影视文件重命名工具，专为群晖Video Station优化，同时支持Windows和macOS系统。增强版在基础功能上新增了强大的API集成功能，能够自动获取准确的影视元数据。

### 🆕 增强版新功能

- **🌐 API集成**: 集成TMDb和豆瓣API，自动获取影视元数据
- **🎯 智能匹配**: 先进的相似度算法，自动选择最佳匹配结果
- **📄 NFO生成**: 自动生成媒体中心元数据文件（支持Kodi、Jellyfin等）
- **🖼️ 海报下载**: 自动下载影片海报和背景图
- **💾 智能缓存**: 元数据缓存机制，避免重复API调用
- **🔤 多语言支持**: 中英文标题智能处理
- **⭐ 评分信息**: 获取TMDb和豆瓣评分
- **🎨 增强模板**: 支持更多元数据变量的命名模板

### 🌟 基础功能保留

- **🔍 智能识别**: 自动提取影片标题、年份、季集、分辨率等信息
- **🎯 精准匹配**: 支持多种文件命名格式和正则表达式规则
- **👀 预览模式**: Dry-run功能，重命名前可预览结果
- **🛡️ 安全保护**: 自动备份、批量限制、文件名验证
- **🔧 灵活配置**: 多种重命名模板，支持自定义
- **🏠 群晖优化**: 专为群晖Video Station设计的命名规范
- **💻 跨平台**: 支持Windows、macOS、Linux、群晖NAS

## 🚀 快速开始

### 1. 自动安装（推荐）

```bash
# 进入工具目录
cd 群晖python版应用

# 运行增强版安装脚本
./install_enhanced_renamer.sh
```

### 2. 手动运行

```bash
# 运行增强版工具
python3 video_renamer_enhanced.py

# 运行演示程序
python3 video_renamer_enhanced_demo.py
```

### 3. API配置

#### TMDb API配置
1. 访问 [TMDb API页面](https://www.themoviedb.org/settings/api)
2. 注册免费账户并申请API密钥
3. 在程序中配置：菜单 4 → 1 → 输入API密钥

#### 豆瓣API配置
1. 在程序中启用：菜单 4 → 2
2. 无需API密钥，但有访问频率限制

## 📋 功能对比

| 功能 | 基础版 | 增强版 |
|------|--------|--------|
| 文件名解析 | ✅ | ✅ |
| 正则表达式提取 | ✅ | ✅ |
| 多种重命名模板 | ✅ | ✅ |
| Dry-run预览 | ✅ | ✅ |
| 跨平台支持 | ✅ | ✅ |
| **TMDb API集成** | ❌ | ✅ |
| **豆瓣API集成** | ❌ | ✅ |
| **NFO文件生成** | ❌ | ✅ |
| **海报下载** | ❌ | ✅ |
| **元数据缓存** | ❌ | ✅ |
| **智能匹配算法** | ❌ | ✅ |
| **评分信息获取** | ❌ | ✅ |
| **增强命名模板** | ❌ | ✅ |

## 🎨 增强版命名模板

### 电影模板示例

#### 1. 增强群晖模板
```
模板: {chinese_title} {title} ({year}) [{resolution}] [{quality}] [评分{rating}].{ext}
示例: 肖申克的救赎 The Shawshank Redemption (1994) [1080p] [BluRay] [评分9.7].mkv
```

#### 2. 元数据丰富模板
```
模板: {title} ({year}) [TMDb{tmdb_rating}] [豆瓣{douban_rating}] [{resolution}].{ext}
示例: The Shawshank Redemption (1994) [TMDb9.3] [豆瓣9.7] [1080p].mkv
```

#### 3. 中文优先模板
```
模板: {chinese_title} ({year}) [{resolution}] [{quality}].{ext}
示例: 肖申克的救赎 (1994) [1080p] [BluRay].mkv
```

### 电视剧模板示例

#### 1. 增强群晖模板
```
模板: {chinese_title} {title} S{season:02d}E{episode:02d} [{resolution}] [{quality}] [评分{rating}].{ext}
示例: 权力的游戏 Game of Thrones S01E01 [1080p] [BluRay] [评分9.3].mkv
```

#### 2. 元数据丰富模板
```
模板: {title} S{season:02d}E{episode:02d} [TMDb{tmdb_rating}] [豆瓣{douban_rating}] [{resolution}].{ext}
示例: Game of Thrones S01E01 [TMDb9.3] [豆瓣9.3] [1080p].mkv
```

### 🔧 增强版模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{chinese_title}` | 中文标题 | 肖申克的救赎 |
| `{title}` | 英文/原始标题 | The Shawshank Redemption |
| `{original_title}` | 原始语言标题 | The Shawshank Redemption |
| `{tmdb_rating}` | TMDb评分 | 9.3 |
| `{douban_rating}` | 豆瓣评分 | 9.7 |
| `{rating}` | 最佳评分 | 9.7 |
| `{director}` | 导演 | Frank Darabont |
| `{genre}` | 类型 | 剧情, 犯罪 |
| `{year}` | 年份 | 1994 |
| `{resolution}` | 分辨率 | 1080p |
| `{quality}` | 画质 | BluRay |

## 📄 NFO文件生成

### 支持的媒体中心
- **Kodi** - 开源媒体中心
- **Jellyfin** - 免费媒体服务器
- **Emby** - 媒体服务器
- **Plex** - 媒体服务器（部分支持）

### NFO文件内容
- 标题（中文/英文/原始）
- 年份和上映日期
- 评分（TMDb/豆瓣）
- 类型和导演
- 演员列表
- 剧情简介
- 外部ID（TMDb/IMDb/豆瓣）

### NFO文件示例
```xml
<?xml version='1.0' encoding='utf-8'?>
<movie>
  <title>肖申克的救赎</title>
  <originaltitle>The Shawshank Redemption</originaltitle>
  <year>1994</year>
  <premiered>1994-09-23</premiered>
  <runtime>142</runtime>
  <plot>银行家安迪因为妻子和她的情人被杀而被判无期徒刑...</plot>
  <director>Frank Darabont</director>
  <rating name="tmdb" max="10">
    <value>8.7</value>
    <votes>24000</votes>
  </rating>
  <rating name="douban" max="10">
    <value>9.7</value>
  </rating>
  <genre>剧情</genre>
  <genre>犯罪</genre>
  <actor>
    <name>Tim Robbins</name>
  </actor>
  <actor>
    <name>Morgan Freeman</name>
  </actor>
  <uniqueid type="tmdb">278</uniqueid>
  <uniqueid type="imdb">tt0111161</uniqueid>
  <uniqueid type="douban">1292052</uniqueid>
</movie>
```

## 🖼️ 海报下载功能

### 支持的图片类型
- **Poster**: 电影海报（竖版，适合封面）
- **Fanart**: 背景图（横版，适合背景）

### 图片尺寸选项
- `w500` - 500px宽度（默认，平衡质量和大小）
- `w780` - 780px宽度（高清）
- `original` - 原始尺寸（最高质量）

### 文件命名规则
```
电影海报: 电影名-poster.jpg
背景图: 电影名-fanart.jpg
```

## 🌐 API集成详解

### TMDb API
- **数据来源**: The Movie Database
- **优势**: 数据全面、更新及时、支持多语言
- **需要**: 免费API密钥
- **限制**: 每秒40次请求
- **获取**: [TMDb API页面](https://www.themoviedb.org/settings/api)

### 豆瓣API
- **数据来源**: 豆瓣电影
- **优势**: 中文数据准确、评分权威
- **需要**: 无需API密钥
- **限制**: 访问频率限制较严格
- **特点**: 主要用于获取中文标题和豆瓣评分

### 智能匹配算法
1. **标题匹配**: 使用编辑距离算法计算相似度
2. **年份匹配**: 考虑年份差异进行评分
3. **流行度加权**: 优先选择更受欢迎的结果
4. **阈值过滤**: 只有匹配度足够高才返回结果

## 💾 缓存机制

### 缓存策略
- **本地存储**: 缓存数据存储在本地JSON文件
- **有效期**: 默认7天，可配置
- **自动清理**: 过期数据自动清理
- **手动清理**: 支持手动清理缓存

### 缓存优势
- **提高速度**: 避免重复API调用
- **节省流量**: 减少网络请求
- **离线使用**: 缓存数据可离线使用
- **降低限制**: 减少API调用频率

## 🎯 使用场景

### 场景1: 整理下载的好莱坞电影

**原始文件名:**
```
The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv
Inception.2010.720p.WEBRip.x264.AAC-YTS.mp4
```

**增强版重命名后:**
```
黑客帝国 The Matrix (1999) [1080p] [BluRay] [评分8.7].mkv
盗梦空间 Inception (2010) [720p] [WEBRip] [评分8.8].mp4
```

### 场景2: 整理中文电影

**原始文件名:**
```
流浪地球.2019.1080p.WEBRip.x264.mkv
我不是药神.2018.720p.BluRay.x264.mp4
```

**增强版重命名后:**
```
流浪地球 (2019) [1080p] [WEBRip] [评分7.9].mkv
我不是药神 (2018) [720p] [BluRay] [评分9.0].mp4
```

### 场景3: 整理美剧

**原始文件名:**
```
Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv
Breaking.Bad.S01E01.720p.BluRay.x264-DEMAND.avi
```

**增强版重命名后:**
```
权力的游戏 Game of Thrones S01E01 [1080p] [BluRay] [评分9.3].mkv
绝命毒师 Breaking Bad S01E01 [720p] [BluRay] [评分9.5].avi
```

## 🔧 高级配置

### API设置优化
```json
{
  "api_settings": {
    "general": {
      "timeout": 15,
      "retry_count": 3,
      "rate_limit_delay": 1.5,
      "cache_enabled": true,
      "cache_expire_days": 14
    }
  }
}
```

### 元数据设置优化
```json
{
  "metadata_settings": {
    "fetch_metadata": true,
    "generate_nfo": true,
    "download_posters": true,
    "prefer_chinese_title": true,
    "metadata_priority": ["tmdb", "douban"],
    "poster_size": "w780",
    "fanart_size": "original"
  }
}
```

## 🛠️ 故障排除

### 常见问题

#### 1. API连接失败
**症状**: 无法获取元数据，显示API连接错误
**解决方案**:
```bash
# 检查网络连接
ping api.themoviedb.org

# 测试API密钥
curl "https://api.themoviedb.org/3/movie/550?api_key=YOUR_API_KEY"

# 重新配置API
程序菜单 -> 4 -> 1 -> 重新输入密钥
```

#### 2. 元数据匹配不准确
**症状**: 获取到错误的电影信息
**解决方案**:
- 确保文件名包含准确的年份信息
- 使用标准的文件命名格式
- 手动清理文件名中的特殊字符

#### 3. NFO文件生成失败
**症状**: 没有生成NFO文件或文件内容为空
**解决方案**:
```bash
# 检查权限
chmod 755 目标目录

# 检查配置
程序菜单 -> 3 -> 查看元数据设置

# 手动测试
程序菜单 -> 5 -> 测试API连接
```

#### 4. 海报下载失败
**症状**: 海报文件没有下载或下载不完整
**解决方案**:
- 检查网络连接稳定性
- 确保有足够的磁盘空间
- 检查目标目录写入权限

### 性能优化

#### 1. 大批量处理
- 分批处理，每批不超过50个文件
- 启用缓存减少重复API调用
- 在网络稳定的环境下处理

#### 2. 网络优化
- 增加API调用间隔时间
- 启用重试机制
- 使用稳定的网络连接

#### 3. 存储优化
- 定期清理过期缓存
- 压缩海报图片大小
- 使用SSD存储提高I/O性能

## 📊 性能对比

| 指标 | 基础版 | 增强版（首次） | 增强版（缓存） |
|------|--------|----------------|----------------|
| 处理速度 | 极快 | 较慢 | 快 |
| 准确度 | 中等 | 很高 | 很高 |
| 功能完整性 | 基础 | 完整 | 完整 |
| 网络依赖 | 无 | 高 | 低 |
| 存储占用 | 最小 | 中等 | 中等 |

## 🏠 群晖NAS专用功能

### Video Station集成
- **目录结构**: 自动创建符合Video Station的目录结构
- **元数据支持**: 生成Video Station识别的NFO文件
- **海报支持**: 下载Video Station显示的海报
- **季度文件夹**: 自动为电视剧创建季度文件夹

### 任务计划支持
```bash
# 创建定时任务脚本
#!/bin/bash
cd /volume1/python_apps/enhanced_video_renamer
python3 video_renamer_enhanced.py --auto-mode --directory /volume1/video
```

### DSM集成
- **文件权限**: 自动设置正确的文件权限
- **用户组**: 支持群晖用户组权限
- **通知**: 可集成群晖通知系统

## 📞 技术支持

### 获取帮助
1. 查看程序内置帮助（菜单选项7）
2. 阅读API配置指南：`API_SETUP_GUIDE.md`
3. 检查日志文件：`logs/video_renamer.log`
4. 运行演示程序了解功能

### 反馈问题
提供以下信息有助于问题诊断：
- 操作系统和Python版本
- API配置状态和网络环境
- 错误日志内容
- 问题文件名示例
- 期望的重命名结果

### 社区支持
- GitHub Issues: 报告bug和功能请求
- 文档更新: 贡献使用经验和最佳实践
- 模板分享: 分享自定义命名模板

## 🔄 版本历史

### v2.0.0 (增强版)
- ✨ 新增TMDb API集成
- ✨ 新增豆瓣API集成
- ✨ 新增NFO文件生成
- ✨ 新增海报下载功能
- ✨ 新增智能匹配算法
- ✨ 新增元数据缓存机制
- ✨ 新增增强版命名模板
- 🔧 优化用户界面和交互体验

### v1.0.0 (基础版)
- ✨ 基础文件名解析功能
- ✨ 正则表达式提取规则
- ✨ 多种重命名模板
- ✨ Dry-run预览功能
- ✨ 跨平台支持
- ✨ 群晖Video Station优化

## 📄 许可证

本项目采用MIT许可证，可以自由使用和修改。

---

**祝你使用愉快！** 🎉

> 💡 **小贴士**: 增强版功能强大但需要网络连接，建议首次使用时先在测试目录中尝试，配置好API后再处理重要文件。