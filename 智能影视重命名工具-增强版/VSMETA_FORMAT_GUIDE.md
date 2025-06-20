# 群晖Video Station vsmeta格式指南

## 📖 概述

vsmeta是群晖Video Station专用的元数据格式，基于JSON结构，用于存储影视作品的详细信息。与标准NFO格式相比，vsmeta格式更适合群晖Video Station的显示和管理需求。

## 🔧 格式对比

| 特性 | NFO格式 | vsmeta格式 |
|------|---------|------------|
| 文件格式 | XML | JSON |
| 适用平台 | Kodi, Jellyfin, Emby | 群晖Video Station |
| 文件扩展名 | .nfo | .vsmeta |
| 中文支持 | 良好 | 优秀 |
| 海报支持 | 需要单独文件 | 内置URL引用 |
| 评分支持 | 多源评分 | 多源评分 |

## 📁 vsmeta文件结构

### 电影vsmeta格式

```json
{
  "version": "1",
  "type": "movie",
  "title": "The Matrix",
  "title_local": "黑客帝国",
  "original_title": "The Matrix",
  "tagline": "Welcome to the Real World",
  "summary": "一名年轻的程序员被神秘的黑客墨菲斯联系...",
  "rating": 8.7,
  "year": 1999,
  "release_date": "1999-03-31",
  "runtime": 136,
  "genre": ["科幻", "动作"],
  "director": ["拉娜·沃卓斯基", "莉莉·沃卓斯基"],
  "writer": ["拉娜·沃卓斯基", "莉莉·沃卓斯基"],
  "actor": [
    {
      "name": "基努·里维斯",
      "role": "尼奥",
      "order": 1
    },
    {
      "name": "劳伦斯·菲什伯恩",
      "role": "墨菲斯",
      "order": 2
    }
  ],
  "extra": {
    "imdb": {
      "id": "tt0133093",
      "rating": 8.7,
      "vote": 1800000
    },
    "tmdb": {
      "id": 603,
      "rating": 8.2,
      "vote": 24000
    },
    "douban": {
      "id": "1291843",
      "rating": 9.0
    }
  },
  "poster": [
    {
      "url": "https://image.tmdb.org/t/p/w500/poster.jpg",
      "type": "poster"
    }
  ],
  "backdrop": [
    {
      "url": "https://image.tmdb.org/t/p/w1280/backdrop.jpg",
      "type": "backdrop"
    }
  ],
  "certificate": "R",
  "country": "美国",
  "language": "英语"
}
```

### 电视剧vsmeta格式

```json
{
  "version": "1",
  "type": "tvshow",
  "title": "Game of Thrones",
  "title_local": "权力的游戏",
  "original_title": "Game of Thrones",
  "tagline": "Winter is Coming",
  "summary": "在维斯特洛大陆上，几个强大的家族为了争夺铁王座...",
  "rating": 9.3,
  "year": 2011,
  "release_date": "2011-04-17",
  "runtime": 60,
  "genre": ["剧情", "奇幻", "冒险"],
  "director": ["大卫·贝尼奥夫", "D·B·威斯"],
  "writer": ["大卫·贝尼奥夫", "D·B·威斯"],
  "actor": [
    {
      "name": "彼特·丁拉基",
      "role": "提利昂·兰尼斯特",
      "order": 1
    }
  ],
  "season": 1,
  "episode": 1,
  "episode_count": 73,
  "season_count": 8,
  "status": "已完结",
  "extra": {
    "tmdb": {
      "id": 1399,
      "rating": 8.3,
      "vote": 22000
    },
    "douban": {
      "id": "3016187",
      "rating": 9.3
    }
  },
  "poster": [
    {
      "url": "https://image.tmdb.org/t/p/w500/poster.jpg",
      "type": "poster"
    }
  ],
  "backdrop": [
    {
      "url": "https://image.tmdb.org/t/p/w1280/backdrop.jpg",
      "type": "backdrop"
    }
  ],
  "certificate": "TV-MA",
  "country": "美国",
  "language": "英语"
}
```

## 🏗️ 字段说明

### 基础字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `version` | string | vsmeta格式版本 | "1" |
| `type` | string | 内容类型 | "movie" / "tvshow" |
| `title` | string | 主标题 | "The Matrix" |
| `title_local` | string | 本地化标题 | "黑客帝国" |
| `original_title` | string | 原始标题 | "The Matrix" |
| `tagline` | string | 宣传语 | "Welcome to the Real World" |
| `summary` | string | 剧情简介 | "一名年轻的程序员..." |
| `rating` | number | 评分 | 8.7 |
| `year` | number | 年份 | 1999 |
| `release_date` | string | 上映日期 | "1999-03-31" |
| `runtime` | number | 时长(分钟) | 136 |

### 人员信息

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `genre` | array | 类型列表 | ["科幻", "动作"] |
| `director` | array | 导演列表 | ["拉娜·沃卓斯基"] |
| `writer` | array | 编剧列表 | ["拉娜·沃卓斯基"] |
| `actor` | array | 演员列表 | [{"name": "基努·里维斯", "role": "尼奥", "order": 1}] |

### 电视剧专用字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `season` | number | 季数 | 1 |
| `episode` | number | 集数 | 1 |
| `episode_count` | number | 总集数 | 73 |
| `season_count` | number | 总季数 | 8 |
| `status` | string | 状态 | "已完结" |

### 扩展信息

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `extra` | object | 外部数据库信息 | {"tmdb": {...}, "douban": {...}} |
| `poster` | array | 海报列表 | [{"url": "...", "type": "poster"}] |
| `backdrop` | array | 背景图列表 | [{"url": "...", "type": "backdrop"}] |
| `certificate` | string | 分级信息 | "R" / "TV-MA" |
| `country` | string | 制片国家 | "美国" |
| `language` | string | 语言 | "英语" |

## 🔧 配置设置

### 启用vsmeta格式

在配置文件中设置：

```json
{
  "metadata_settings": {
    "generate_nfo": true,
    "nfo_format": "vsmeta"
  }
}
```

### 程序中切换格式

在增强版重命名工具中：

1. 进入程序菜单
2. 选择 "4. 配置API设置"
3. 选择 "3. 元数据设置"
4. 切换NFO格式为vsmeta

## 📁 群晖Video Station目录结构

### 电影目录结构

```
/volume1/video/Movies/
├── 黑客帝国 The Matrix (1999)/
│   ├── 黑客帝国 The Matrix (1999) [1080p] [BluRay] [评分8.7].mkv
│   ├── 黑客帝国 The Matrix (1999) [1080p] [BluRay] [评分8.7].vsmeta
│   ├── 黑客帝国 The Matrix (1999) [1080p] [BluRay] [评分8.7]-poster.jpg
│   └── 黑客帝国 The Matrix (1999) [1080p] [BluRay] [评分8.7]-fanart.jpg
```

### 电视剧目录结构

```
/volume1/video/TV Shows/
├── 权力的游戏 Game of Thrones (2011)/
│   ├── Season 01/
│   │   ├── 权力的游戏 Game of Thrones S01E01 [1080p] [BluRay] [评分9.3].mkv
│   │   ├── 权力的游戏 Game of Thrones S01E01 [1080p] [BluRay] [评分9.3].vsmeta
│   │   └── ...
│   ├── Season 02/
│   │   └── ...
│   ├── tvshow_info.vsmeta
│   ├── poster.jpg
│   └── fanart.jpg
```

## 🎯 vsmeta格式优势

### 1. 群晖原生支持
- Video Station完美识别
- 无需额外插件或配置
- 显示效果最佳

### 2. 中文支持优秀
- `title_local`字段专门存储中文标题
- 支持中英文双标题显示
- 中文演员、导演信息完整支持

### 3. 多源评分整合
- 同时支持TMDb、豆瓣、IMDb评分
- 评分信息在Video Station中正确显示
- 支持投票数等详细信息

### 4. 海报集成
- 海报URL直接存储在vsmeta文件中
- Video Station自动获取和显示海报
- 支持多种尺寸的海报和背景图

## 🛠️ 使用建议

### 1. 群晖用户
- **推荐使用vsmeta格式**
- 设置 `nfo_format: "vsmeta"`
- 启用 `create_synology_structure: true`

### 2. 其他媒体中心用户
- Kodi/Jellyfin用户使用NFO格式
- 设置 `nfo_format: "nfo"`
- 可以同时生成两种格式

### 3. 混合环境
- 可以为不同目录设置不同格式
- 使用脚本批量转换格式
- 保持目录结构的一致性

## 🔄 格式转换

### NFO转vsmeta

```python
# 使用工具内置的转换功能
python3 video_renamer_enhanced.py --convert-format nfo-to-vsmeta --directory /path/to/videos
```

### vsmeta转NFO

```python
# 使用工具内置的转换功能
python3 video_renamer_enhanced.py --convert-format vsmeta-to-nfo --directory /path/to/videos
```

## 🐛 故障排除

### 常见问题

#### 1. vsmeta文件不被识别
**解决方案:**
- 检查文件编码是否为UTF-8
- 验证JSON格式是否正确
- 确认文件权限设置

#### 2. 中文显示乱码
**解决方案:**
- 确保vsmeta文件使用UTF-8编码
- 检查群晖系统语言设置
- 重启Video Station服务

#### 3. 海报不显示
**解决方案:**
- 检查海报URL是否有效
- 确认网络连接正常
- 验证海报文件大小和格式

### 调试方法

#### 1. 验证vsmeta格式
```bash
# 使用jq验证JSON格式
cat movie.vsmeta | jq .

# 检查文件编码
file -i movie.vsmeta
```

#### 2. 查看Video Station日志
```bash
# 群晖系统日志位置
tail -f /var/log/synolog/synoindex.log
```

## 📚 参考资源

- [群晖Video Station官方文档](https://www.synology.com/zh-cn/dsm/feature/video_station)
- [JSON格式验证工具](https://jsonlint.com/)
- [群晖开发者文档](https://www.synology.com/zh-cn/support/developer)

---

**vsmeta格式让群晖Video Station发挥最佳效果！** 🎉

> 💡 **提示**: 群晖用户强烈推荐使用vsmeta格式，可以获得最佳的元数据显示效果和中文支持。