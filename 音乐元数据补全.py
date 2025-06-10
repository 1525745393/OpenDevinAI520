import os
import re
import logging
import argparse
import time
import requests
from mutagen import File
import concurrent.futures

# ============ 配置 ==============
LASTFM_API_KEY = "fa4db6d9a7da2b1b581848e97a37d417"
LOG_FILE = "music_metadata.log"
DEFAULT_FOLDER = "./flac_music_folder"
DEFAULT_MAX_WORKERS = 8
AUDIO_EXTENSIONS = ['.flac', '.mp3', '.ape', '.wav', '.m4a', '.ogg', '.aac']
# ================================

# ---- 日志系统初始化（文件+控制台） ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ---- 查询缓存 ----
metadata_cache = {}

# ---- 文件名智能解析函数 ----
def clean_filename(name_part: str) -> str:
    """去除常见无用修饰信息和括号内容"""
    name_part = re.sub(r'[\[\(\{【（『「][^\]\)\}】）』」]*[\]\)\}】）』」]', '', name_part)
    name_part = re.sub(
        r'(官方|无损|320K|MV|FLAC|APE|WAV|mp3|伴奏|现场|原版|试听版|Live|Remix|Demo|Acoustic|Edit|Mix|Session|KTV|伴唱|纯音乐|Instrumental|版|正版|HQ|HD|Hi-Res|HiRes|DSD|Single|EP|专辑|CD\d+|DISC\d+|数字专辑|数字音频|母带)',
        '', name_part, flags=re.I)
    return name_part.strip()

def extract_keywords(filename: str):
    """
    智能解析文件名，返回 歌名, 歌手, 置信度
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    name_part = clean_filename(base)
    delimiters = [
        ' - ', '-', '_', '–', '—', '|', ':', '：', '.', '·', '/', '\\', ' feat. ', ' ft. ', ' Feat ', ' Ft ', '&'
    ]
    confidence = 0.3
    feat_match = re.match(r'(.+?)\s*(?:feat\.|ft\.|Feat|Ft)\s*(.+)', name_part, re.I)
    if feat_match:
        artist, title = feat_match.groups()
        confidence = 0.95
        return title.strip(), artist.strip(), confidence
    for delim in delimiters:
        if delim in name_part:
            parts = [p.strip() for p in name_part.split(delim) if p.strip()]
            if len(parts) == 2:
                if len(parts[0]) <= 8 and len(parts[1]) > 1:
                    confidence = 0.85
                    return parts[1], parts[0], confidence
                else:
                    confidence = 0.8
                    return parts[0], parts[1], confidence
            elif len(parts) > 2:
                confidence = 0.6
                return parts[-1], " & ".join(parts[:-1]), confidence
    match1 = re.match(r'(.+)[《](.+)[》]', name_part)
    if match1:
        artist, title = match1.groups()
        confidence = 0.9
        return title.strip(), artist.strip(), confidence
    match2 = re.match(r'(.+)[（(](.+)[)）]', name_part)
    if match2:
        title, artist = match2.groups()
        confidence = 0.85
        return title.strip(), artist.strip(), confidence
    confidence = 0.4
    return name_part, None, confidence

# ---- 网络请求自动重试 ----
def robust_request(url, params=None, headers=None, retries=3, delay=2):
    for i in range(retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.ok:
                return resp
        except Exception as e:
            logging.warning("第%d次请求异常: %s", i+1, e)
        time.sleep(delay)
    return None

# ---- MusicBrainz 查询 ----
def search_musicbrainz(title, artist=None):
    cache_key = ("MB", title or "", artist or "")
    if cache_key in metadata_cache:
        logging.debug("MusicBrainz缓存命中: %s", cache_key)
        return metadata_cache[cache_key]
    query = f'recording:"{title}"'
    if artist:
        query += f' AND artist:"{artist}"'
    url = 'https://musicbrainz.org/ws/2/recording/'
    headers = {'User-Agent': 'MetaTagger/1.0 (your@email.com)'}
    params = {'query': query, 'fmt': 'json'}
    resp = robust_request(url, params=params, headers=headers)
    if resp:
        try:
            data = resp.json()
            if data.get('recordings'):
                rec = data['recordings'][0]
                result = {
                    'title': rec.get('title'),
                    'artist': rec['artist-credit'][0]['name'],
                    'album': rec['releases'][0]['title'] if rec.get('releases') else '',
                    'date': rec['releases'][0].get('date', '') if rec.get('releases') else '',
                }
                metadata_cache[cache_key] = result
                return result
        except Exception as e:
            logging.error("MusicBrainz数据解析错误: %s", e)
    metadata_cache[cache_key] = {}
    return {}

# ---- Last.fm 查询 ----
def search_lastfm(title, artist):
    cache_key = ("LF", title or "", artist or "")
    if cache_key in metadata_cache:
        logging.debug("Last.fm缓存命中: %s", cache_key)
        return metadata_cache[cache_key]
    if not title or not artist:
        return {}
    params = {
        "method": "track.getInfo",
        "api_key": LASTFM_API_KEY,
        "artist": artist,
        "track": title,
        "format": "json"
    }
    resp = robust_request("https://ws.audioscrobbler.com/2.0/", params=params)
    if resp:
        try:
            data = resp.json()
            if "track" in data:
                track = data["track"]
                result = {
                    "title": track.get("name"),
                    "artist": track.get("artist", {}).get("name"),
                    "album": track.get("album", {}).get("title", ''),
                    "date": ''
                }
                metadata_cache[cache_key] = result
                return result
        except Exception as e:
            logging.error("Last.fm数据解析错误: %s", e)
    metadata_cache[cache_key] = {}
    return {}

# ---- 具体元数据补全 ----
def fill_metadata(audio_path):
    try:
        audio = File(audio_path, easy=True)
        if audio is None or audio.tags is None:
            logging.warning("[跳过] 不支持或损坏的文件: %s", audio_path)
            return
        missing = [field for field in ['title', 'artist', 'album'] if field not in audio or not audio[field]]
        if not missing:
            logging.debug("跳过已有元数据: %s", os.path.basename(audio_path))
            return
        title, artist, conf = extract_keywords(audio_path)
        logging.info("解析: %s | 歌名=%s 歌手=%s 置信度=%.2f", os.path.basename(audio_path), title, artist, conf)
        if conf < 0.5:
            logging.warning("文件名解析置信度低: %s (%.2f)", audio_path, conf)
        result = search_musicbrainz(title, artist)
        if not result:
            logging.info("MusicBrainz未命中，尝试Last.fm: %s", os.path.basename(audio_path))
            result = search_lastfm(title, artist)
        if result:
            for k, v in result.items():
                if v and (k not in audio or not audio[k]):
                    audio[k] = v
            audio.save()
            logging.info("成功补全: %s → %s", os.path.basename(audio_path), result)
        else:
            logging.warning("未能补全: %s", os.path.basename(audio_path))
    except Exception as e:
        logging.error("处理异常: %s | %s", audio_path, e)

# ---- 目录批量并发处理 ----
def process_folder_parallel(folder, max_workers=DEFAULT_MAX_WORKERS):
    audio_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[1].lower() in AUDIO_EXTENSIONS:
                audio_files.append(os.path.join(root, file))
    if not audio_files:
        logging.warning("未发现音频文件于目录: %s", folder)
        return
    workers = max(1, min(max_workers, len(audio_files)//5 + 1))
    logging.info("批量处理音频文件: %d个，线程数: %d", len(audio_files), workers)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        list(executor.map(fill_metadata, audio_files))

# ---- 命令行参数支持 ----
def main():
    parser = argparse.ArgumentParser(description="批量补全音乐元数据（FLAC/MP3/APE/WAV/M4A/OGG/AAC等）")
    parser.add_argument('-f', '--folder', type=str, default=DEFAULT_FOLDER, help="音频目录路径")
    parser.add_argument('-w', '--max-workers', type=int, default=DEFAULT_MAX_WORKERS, help="最大线程数")
    args = parser.parse_args()
    process_folder_parallel(args.folder, args.max_workers)

if __name__ == "__main__":
    main()