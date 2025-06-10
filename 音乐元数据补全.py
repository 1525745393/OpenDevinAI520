import os
import re
import requests
from mutagen.flac import FLAC

# 你的 Last.fm API 密钥
LASTFM_API_KEY = "fa4db6d9a7da2b1b581848e97a37d417"

def extract_keywords(filename):
    """从文件名中猜测歌名和歌手"""
    name_part = os.path.splitext(os.path.basename(filename))[0]
    match = re.match(r"(.+)[-_ ]+(.+)", name_part)
    if match:
        part1, part2 = match.groups()
        return [part1.strip(), part2.strip()]
    return [name_part.strip(), None]

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
    audio = FLAC(flac_path)
    missing = [field for field in ['title', 'artist', 'album'] if field not in audio or not audio[field][0].strip()]
    if not missing:
        print(f"[✓] 已有元数据：{os.path.basename(flac_path)}")
        return

    title, artist = extract_keywords(flac_path)
    print(f"[…] 尝试补全：{os.path.basename(flac_path)}")

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

def process_folder(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".flac"):
                fill_metadata(os.path.join(root, file))

# 修改此处路径为你的 FLAC 文件夹路径
if __name__ == "__main__":
    folder_path = "./flac_music_folder"
    process_folder(folder_path)