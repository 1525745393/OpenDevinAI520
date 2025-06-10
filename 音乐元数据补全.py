import os
import re
import requests
from mutagen.flac import FLAC
import concurrent.futures

# 你的 Last.fm API 密钥
LASTFM_API_KEY = "fa4db6d9a7da2b1b581848e97a37d417"

def extract_keywords(filename):
    """更智能地从文件名中猜测歌名和歌手"""
    name_part = os.path.splitext(os.path.basename(filename))[0]
    # 去除常见无关修饰
    name_part = re.sub(r'[\[\(【（].*?[\]\)】）]', '', name_part)
    name_part = re.sub(r'(官方|无损|320K|MV|FLAC|mp3|伴奏|现场|原版|官方版|试听版|Live|版)', '', name_part, flags=re.I)
    name_part = name_part.strip()

    # 常见分隔符
    delimiters = [' - ', '-', '_', '–', '—', '|', ':', '：', '.', '·']
    for delim in delimiters:
        if delim in name_part:
            parts = [p.strip() for p in name_part.split(delim) if p.strip()]
            # 优先两段的情况
            if len(parts) == 2:
                # 猜测哪个是歌手，哪个是歌名
                if len(parts[0]) < 8 and len(parts[1]) > 1:  # 大概率歌手在前
                    return [parts[1], parts[0]]
                else:
                    return [parts[0], parts[1]]
    # 特殊情况如：歌手《歌名》
    match = re.match(r'(.+)[《](.+)[》]', name_part)
    if match:
        artist, title = match.groups()
        return [title.strip(), artist.strip()]
    # 特殊情况如：歌名（歌手）
    match = re.match(r'(.+)[（(](.+)[)）]', name_part)
    if match:
        title, artist = match.groups()
        return [title.strip(), artist.strip()]
    # 实在无法拆分，默认整段为歌名
    return [name_part, None]

def search_musicbrainz(title, artist=None):
    """使用 MusicBrainz 搜索歌曲元数据"""
    query = f'recording:"{title}"'
    if artist:
        query += f' AND artist:"{artist}"'
    url = f'https://musicbrainz.org/ws/2/recording/?query={query}&fmt=json'
    headers = {'User-Agent': 'MetaTagger/1.0 (your@email.com)'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.ok:
            data = resp.json()
            if data.get('recordings'):
                rec = data['recordings'][0]
                return {
                    'title': rec.get('title'),
                    'artist': rec['artist-credit'][0]['name'],
                    'album': rec['releases'][0]['title'] if rec.get('releases') else '',
                    'date': rec['releases'][0].get('date', '') if rec.get('releases') else '',
                }
    except Exception as e:
        print(f"[!] MusicBrainz 请求失败: {e}")
    return {}

def search_lastfm(title, artist):
    """使用 Last.fm API 补全歌曲信息"""
    if not title or not artist:
        return {}
    params = {
        "method": "track.getInfo",
        "api_key": LASTFM_API_KEY,
        "artist": artist,
        "track": title,
        "format": "json"
    }
    try:
        resp = requests.get("https://ws.audioscrobbler.com/2.0/", params=params, timeout=10)
        if resp.ok:
            data = resp.json()
            if "track" in data:
                track = data["track"]
                return {
                    "title": track.get("name"),
                    "artist": track.get("artist", {}).get("name"),
                    "album": track.get("album", {}).get("title", ''),
                    "date": ''  # Last.fm 无法提供精确发行时间
                }
    except Exception as e:
        print(f"[!] Last.fm 请求失败: {e}")
    return {}

def fill_metadata(flac_path):
    try:
        audio = FLAC(flac_path)
        missing = [field for field in ['title', 'artist', 'album'] if field not in audio or not audio[field][0].strip()]
        if not missing:
            print(f"[✓] 已有元数据：{os.path.basename(flac_path)}")
            return

        title, artist = extract_keywords(flac_path)
        print(f"[…] 尝试补全：{os.path.basename(flac_path)} | 猜测: 歌名={title} 歌手={artist}")

        result = search_musicbrainz(title, artist)
        if not result:
            print("    ⤷ MusicBrainz 未命中，尝试 Last.fm…")
            result = search_lastfm(title, artist)

        if result:
            for k, v in result.items():
                if v and (k not in audio or not audio[k]):
                    audio[k] = v
            audio.save()
            print(f"[+] 成功补全：{os.path.basename(flac_path)} → {result}")
        else:
            print(f"[×] 补全失败：{os.path.basename(flac_path)}")
    except Exception as e:
        print(f"[!] 处理文件时出错 {flac_path}: {e}")

def process_folder_parallel(folder, max_workers=8):
    flac_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".flac"):
                flac_files.append(os.path.join(root, file))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(fill_metadata, flac_files))

# 修改此处路径为你的 FLAC 文件夹路径
if __name__ == "__main__":
    folder_path = "./flac_music_folder"
    process_folder_parallel(folder_path)