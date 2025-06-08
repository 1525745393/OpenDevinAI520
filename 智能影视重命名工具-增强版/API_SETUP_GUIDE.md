# API设置指南 - 增强版重命名工具

## 📖 概述

增强版智能影视文件重命名工具集成了TMDb和豆瓣API，可以自动获取准确的影视元数据，包括中文标题、评分、海报、剧情简介等信息。

## 🌐 支持的API

### 1. TMDb (The Movie Database)
- **类型**: 国际影视数据库
- **优势**: 数据全面、更新及时、支持多语言
- **需要**: 免费API密钥
- **限制**: 每秒40次请求

### 2. 豆瓣电影
- **类型**: 中文影视数据库  
- **优势**: 中文数据准确、评分权威
- **需要**: 无需API密钥
- **限制**: 访问频率限制较严格

## 🔧 TMDb API配置

### 步骤1: 注册账户

1. 访问 [TMDb官网](https://www.themoviedb.org/)
2. 点击右上角 "Join TMDb" 注册账户
3. 填写用户名、邮箱、密码完成注册
4. 验证邮箱激活账户

### 步骤2: 申请API密钥

1. 登录后访问 [API设置页面](https://www.themoviedb.org/settings/api)
2. 点击 "Create" 创建新的API密钥
3. 选择 "Developer" 类型
4. 填写应用信息：
   ```
   Application Name: Video Renamer Tool
   Application URL: https://github.com/your-repo
   Application Summary: 智能影视文件重命名工具
   ```
5. 同意服务条款，提交申请
6. 复制生成的API密钥（v3 auth）

### 步骤3: 配置工具

1. 运行重命名工具
2. 选择 "4. 配置API设置"
3. 选择 "1. 配置TMDb API"
4. 粘贴API密钥
5. 测试连接确认配置成功

### API密钥示例
```
API密钥格式: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
长度: 32位字符
```

## 🎭 豆瓣API配置

### 特点说明
- **无需注册**: 直接启用即可使用
- **访问限制**: 有频率限制，建议适度使用
- **数据质量**: 中文数据准确，评分权威

### 配置步骤
1. 运行重命名工具
2. 选择 "4. 配置API设置"
3. 选择 "2. 启用/禁用豆瓣API"
4. 选择启用
5. 测试连接确认可用

### 使用建议
- 主要用于获取中文标题和豆瓣评分
- 与TMDb配合使用效果最佳
- 大批量处理时建议降低频率

## ⚙️ 配置文件详解

### API设置部分
```json
{
  "api_settings": {
    "tmdb": {
      "enabled": true,
      "api_key": "your_tmdb_api_key_here",
      "language": "zh-CN",
      "region": "CN"
    },
    "douban": {
      "enabled": true
    },
    "general": {
      "timeout": 10,
      "retry_count": 3,
      "rate_limit_delay": 1.0,
      "cache_enabled": true,
      "cache_expire_days": 7
    }
  }
}
```

### 元数据设置部分
```json
{
  "metadata_settings": {
    "fetch_metadata": true,
    "generate_nfo": true,
    "download_posters": true,
    "download_fanart": true,
    "prefer_chinese_title": true,
    "fallback_to_original": true,
    "metadata_priority": ["tmdb", "douban"],
    "poster_size": "w500",
    "fanart_size": "w1280"
  }
}
```

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

### 可用变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `{chinese_title}` | 中文标题 | 肖申克的救赎 |
| `{title}` | 英文/原始标题 | The Shawshank Redemption |
| `{original_title}` | 原始语言标题 | The Shawshank Redemption |
| `{year}` | 年份 | 1994 |
| `{tmdb_rating}` | TMDb评分 | 9.3 |
| `{douban_rating}` | 豆瓣评分 | 9.7 |
| `{rating}` | 最佳评分 | 9.7 |
| `{director}` | 导演 | Frank Darabont |
| `{genre}` | 类型 | 剧情, 犯罪 |
| `{resolution}` | 分辨率 | 1080p |
| `{quality}` | 画质 | BluRay |

## 📄 NFO文件生成

### 什么是NFO文件
NFO文件是媒体中心（如Kodi、Jellyfin、Emby）使用的元数据文件，包含影片的详细信息。

### 生成的NFO内容
- 标题（中文/英文）
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

## 🖼️ 海报下载

### 支持的图片类型
- **Poster**: 电影海报（竖版）
- **Fanart**: 背景图（横版）

### 图片尺寸选项
- `w92` - 92px宽度（缩略图）
- `w154` - 154px宽度（小图）
- `w185` - 185px宽度（中图）
- `w342` - 342px宽度（大图）
- `w500` - 500px宽度（高清）
- `w780` - 780px宽度（超清）
- `original` - 原始尺寸

### 文件命名规则
```
电影海报: 电影名-poster.jpg
背景图: 电影名-fanart.jpg
```

## 🚀 使用流程

### 1. 首次配置
```bash
# 运行程序
python3 video_renamer_enhanced.py

# 选择配置API
4 -> 1 -> 输入TMDb API密钥
4 -> 2 -> 启用豆瓣API

# 测试连接
5 -> 确认API可用
```

### 2. 预览重命名
```bash
# 选择预览模式
1 -> 输入目录路径 -> 查看预览结果
```

### 3. 执行重命名
```bash
# 选择重命名模式
2 -> 输入目录路径 -> 确认执行
```

## 🛠️ 故障排除

### 常见问题

#### 1. TMDb API连接失败
**可能原因:**
- API密钥错误或过期
- 网络连接问题
- 超出API调用限制

**解决方案:**
```bash
# 检查API密钥
curl "https://api.themoviedb.org/3/movie/550?api_key=YOUR_API_KEY"

# 重新配置API密钥
程序菜单 -> 4 -> 1 -> 重新输入密钥
```

#### 2. 豆瓣API访问受限
**可能原因:**
- 访问频率过高
- IP被临时限制
- 网络连接问题

**解决方案:**
```bash
# 降低访问频率
配置文件 -> api_settings.general.rate_limit_delay = 2.0

# 暂时禁用豆瓣API
程序菜单 -> 4 -> 2 -> 禁用
```

#### 3. 元数据匹配不准确
**可能原因:**
- 文件名格式不标准
- 标题包含特殊字符
- 年份信息缺失

**解决方案:**
```bash
# 手动清理文件名
重命名为标准格式: 电影名.年份.其他信息.扩展名

# 调整匹配阈值
配置文件中修改相似度算法参数
```

#### 4. NFO文件生成失败
**可能原因:**
- 权限不足
- 磁盘空间不足
- 文件路径包含特殊字符

**解决方案:**
```bash
# 检查权限
chmod 755 目标目录

# 检查磁盘空间
df -h

# 避免特殊字符
使用英文路径和文件名
```

### 日志分析

#### 查看详细日志
```bash
# 查看实时日志
tail -f logs/video_renamer.log

# 搜索错误信息
grep "ERROR" logs/video_renamer.log

# 搜索API相关日志
grep "API" logs/video_renamer.log
```

#### 常见日志信息
```
INFO - 从TMDb搜索电影: The Matrix
INFO - TMDb获取成功: The Matrix (1999)
WARNING - 豆瓣API访问受限，稍后重试
ERROR - TMDb API错误: Invalid API key
```

## 📊 性能优化

### 1. 缓存策略
- 启用元数据缓存避免重复API调用
- 缓存有效期默认7天
- 手动清理缓存: 程序菜单 -> 6

### 2. 批处理建议
- 单次处理建议不超过100个文件
- 大批量处理时分批进行
- 网络不稳定时降低并发数

### 3. API调用优化
- 设置合理的请求间隔
- 启用重试机制
- 优先使用缓存数据

## 🔒 安全注意事项

### 1. API密钥保护
- 不要在公开场所分享API密钥
- 定期更换API密钥
- 使用环境变量存储敏感信息

### 2. 网络安全
- 使用HTTPS连接
- 避免在不安全网络环境下使用
- 定期更新程序版本

### 3. 数据隐私
- API调用会发送文件名信息
- 不会上传实际文件内容
- 缓存数据存储在本地

## 📞 技术支持

### 获取帮助
1. 查看程序内置帮助（菜单选项7）
2. 检查日志文件错误信息
3. 验证API配置和网络连接
4. 参考本指南故障排除部分

### 反馈问题
提供以下信息有助于问题诊断：
- 操作系统和Python版本
- API配置状态
- 错误日志内容
- 问题文件名示例
- 网络环境信息

---

**祝你使用愉快！** 🎉

> 💡 **小贴士**: 建议首次使用时先在测试目录中尝试，熟悉API功能后再处理重要文件。