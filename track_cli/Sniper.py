#!/usr/bin/env python3
import os
import re
import glob
import requests
from urllib.parse import quote_plus
import yt_dlp
import sys
from mutagen.oggopus import OggOpus

# --- ANSI TERMINAL COLORS ---
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"

# --- SYSTEM AGNOSTIC STORAGE TARGET ---

HOME_DIR = os.path.expanduser("~")

# Checks if it's running inside Android Termux, otherwise falls back to Desktop Music folder

if os.path.exists("/data/data/com.termux/files/home/"):
    TARGET_DIR = "/data/data/com.termux/files/home/storage/shared/Music/"

else:
    TARGET_DIR = os.path.join(HOME_DIR, "Music", "Downloads")


def print_status(color, prefix, message):
    print(f"{color}{prefix} {message}{RESET}")

def fetch_lrclib_lyrics(artist, title):
    """Queries LRCLIB with strict fallback matching hierarchy."""
    print_status(CYAN, "[*]", f"Scanning LRCLIB API for: {artist} - {title}...")
    query = f"{artist} {title}"
    url = f"https://lrclib.net/api/search?q={quote_plus(query)}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print_status(RED, "[!]", f"LRCLIB error code: {response.status_code}")
            return None
        
        results = response.json()
        if not results:
            return None

        # Pass 1: Strict Synced Priority
        for track in results:
            if track.get('syncedLyrics'):
                print_status(GREEN, "[✓]", "Time-synchronized lyrics matched!")
                return track['syncedLyrics']
                
        # Pass 2: Plain Text Fallback
        for track in results:
            if track.get('plainLyrics'):
                print_status(YELLOW, "[!]", "Synced lyrics missing. Using plain text lyrics.")
                return track['plainLyrics']
                
    except Exception as e:
        print_status(RED, "[!]", f"LRCLIB Network lookup failed: {e}")
    return None

def parse_vtt_to_lrc(vtt_path):
    """Converts a standard WebVTT closed caption file into clean LRC format."""
    lrc_lines = []
    time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})')
    
    if not os.path.exists(vtt_path):
        return None
        
    with open(vtt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        match = time_pattern.match(line.strip())
        if match and (i + 1) < len(lines):
            min_val = int(match.group(2)) + (int(match.group(1)) * 60)
            sec_val = match.group(3)
            ms_val = match.group(4)[:2]
            
            timestamp = f"[{min_val:02d}:{sec_val}.{ms_val}]"
            text_line = lines[i+1].strip()
            
            if text_line and not text_line.startswith('NOTE') and not text_line.isdigit():
                text_line = re.sub(r'<[^>]*>', '', text_line)
                lrc_lines.append(f"{timestamp} {text_line}")
                
    return "\n".join(lrc_lines) if lrc_lines else None

def main():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    # 1. INPUT PIPELINE (Accepts arguments or drops back to input prompt)
    if len(sys.argv) > 1:
        url = sys.argv[1].strip()
        print_status(GREEN, "[✓]", f"Intercepted URL via argument: {url}")
    else:
        url = input(f"{CYAN}Enter YouTube URL: {RESET}").strip()
        
    if not url or not url.startswith(("http://", "https://")):
        print_status(RED, "[!]", "Validation Error: Invalid URL.")
        return



    use_subs = input(f"{CYAN}Force extract YouTube native closed captions? (y/N): {RESET}").strip().lower() == 'y'

    # 2. CONFIGURE EXTRACTION WITH FILE SANITIZATION
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(TARGET_DIR, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'postprocs': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '0',
            },
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ],
        'writethumbnails': True,
        'quiet': True,
        'no_warnings': True,
    }

    if use_subs:
        ydl_opts['writesubtitles'] = True
        ydl_opts['writeautomaticsub'] = True
        ydl_opts['subtitleslangs'] = ['en']

    print_status(CYAN, "[*]", "Spinning up extraction engine streams...")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as e:
            print_status(RED, "[!]", f"Extraction or download engine failure: {e}")
            return

    # Bulletproof Dynamic File Lookup: Find the latest updated .opus file in the target directory
    opus_files = glob.glob(os.path.join(TARGET_DIR, "*.opus"))
    if not opus_files:
        print_status(RED, "[!]", "Error: No output audio track detected in destination.")
        return
    opus_path = max(opus_files, key=os.path.getmtime)

    # 3. INTERMEDIATE TAG METADATA READING
    print_status(CYAN, "[*]", f"Reading file tags from: {os.path.basename(opus_path)}")
    try:
        audio = OggOpus(opus_path)
        title = audio.get("title", [info.get("title")])[0]
        artist = audio.get("artist", [info.get("uploader")])[0]
    except Exception as e:
        title = info.get("title")
        artist = info.get("uploader", "")

    # 4. LYRICS EXTRACTION & PARSING ROUTE
    lyrics = None

    if use_subs:
        print_status(CYAN, "[*]", "Scanning for downloaded native closed captions...")
        base_no_ext = os.path.splitext(opus_path)[0]
        # Look for downloaded subtitle files matching the scrubbed base path
        vtt_files = glob.glob(base_no_ext + "*.vtt")
        if vtt_files:
            vtt_path = vtt_files[0]
            lyrics = parse_vtt_to_lrc(vtt_path)
            if lyrics:
                print_status(GREEN, "[✓]", "Parsed YouTube closed captions into synchronized LRC layout.")
            os.remove(vtt_path)

    if not lyrics:
        lyrics = fetch_lrclib_lyrics(artist, title)

    # 5. VORBIS COMMENT INJECTION
    if lyrics:
        try:
            audio = OggOpus(opus_path)
            audio["LYRICS"] = lyrics
            audio.save()
            print_status(GREEN, "[✓]", "Lyrics compiled directly into the file's LYRICS tab!")
        except Exception as e:
            print_status(RED, "[!]", f"Failed to map lyrics structure into file header: {e}")
    else:
        print_status(YELLOW, "[!]", "No lyrics fields generated. Leaving container file unmodified.")

    print_status(GREEN, "[✓]", f"Pipeline complete! Track locked at: {opus_path}\n")

if __name__ == "__main__":
    main()
